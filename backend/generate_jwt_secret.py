import secrets
import os

def generate_jwt_secret():
    # Generate a secure random string of 32 bytes and convert to hex
    jwt_secret = secrets.token_hex(32)
    
    # Path to .env file
    env_path = '.env'
    
    try:
        # Read existing .env content
        env_content = {}
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        env_content[key] = value

        # Update or add JWT_SECRET
        env_content['JWT_SECRET'] = f'"{jwt_secret}"'
        
        # Write back to .env file
        with open(env_path, 'w') as f:
            for key, value in env_content.items():
                f.write(f'{key}={value}\n')
            
        print(f'JWT_SECRET has been generated and written to {env_path}')
        
    except Exception as e:
        print(f'Error writing to .env file: {str(e)}')
        return None

if __name__ == '__main__':
    generate_jwt_secret()