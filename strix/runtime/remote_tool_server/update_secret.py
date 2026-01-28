import sys
import base64
import requests
from nacl import encoding, public

def encrypt(public_key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key."""
    public_key_obj = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key_obj)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def update_secret(token, owner, repo, name, value):
    """
    1. Get the public key for Actions secrets
    2. Encrypt the secret value
    3. Update the secret via GitHub API
    """
    # 1. Get the public key
    pub_key_url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/public-key"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(pub_key_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to get public key: {response.text}")
        response.raise_for_status()
        
    key_data = response.json()
    key_id = key_data["key_id"]
    public_key = key_data["key"]

    # 2. Encrypt the secret
    encrypted_value = encrypt(public_key, value)

    # 3. Update the secret
    update_url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/{name}"
    data = {
        "encrypted_value": encrypted_value,
        "key_id": key_id,
    }
    response = requests.put(update_url, headers=headers, json=data)
    if response.status_code not in [201, 204]:
        print(f"Failed to update secret: {response.text}")
        response.raise_for_status()

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python3 -m strix.runtime.remote_tool_server.update_secret <token> <owner> <repo> <name> <value>")
        sys.exit(1)
    
    token_arg, owner_arg, repo_arg, name_arg, value_arg = sys.argv[1:]
    try:
        update_secret(token_arg, owner_arg, repo_arg, name_arg, value_arg)
        print(f"Successfully updated GitHub secret: {name_arg}")
    except Exception as e:
        print(f"Error updating secret: {e}")
        sys.exit(1)
