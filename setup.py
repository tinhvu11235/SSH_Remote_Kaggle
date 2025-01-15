import os
import subprocess

def start_ssh(id_rsa_pub="", password="", install_ssh=False, config_ssh=False):
    """
    Setup and ensure SSH is running in a Docker container.
    """
    def log_step(step):
        print(f"[INFO] {step}")

    def check_error(command, step):
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] {step} failed. Error: {result.stderr.strip()}")
        return result.returncode

    log_step("***** SETUP SSH SERVICE IN DOCKER *****")

    # Step 1: Install SSH service
    if install_ssh:
        log_step("Installing SSH service...")
        if check_error('apt-get update && apt-get install openssh-server -y', "Install SSH service") != 0:
            return False

    # Step 2: Add public key
    if id_rsa_pub:
        log_step("Adding public key to authorized keys...")
        os.makedirs(os.path.expanduser("~/.ssh"), exist_ok=True)
        with open(os.path.expanduser("~/.ssh/authorized_keys"), "a") as f:
            f.write(id_rsa_pub + "\n")
        log_step("Public key added successfully.")

    # Step 3: Configure SSH service
    if config_ssh:
        log_step("Configuring SSH service...")
        commands = [
            "sed -i 's/^#Port.*/Port 22/' /etc/ssh/sshd_config",
            "sed -i 's/^PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config",
            "sed -i 's/^#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config",
            "sed -i 's/^#PubkeyAuthentication.*/PubkeyAuthentication yes/' /etc/ssh/sshd_config",
        ]
        for command in commands:
            if check_error(command, "Configure SSH service") != 0:
                return False
        log_step("SSH configuration updated successfully.")

    # Step 4: Set root password
    if password:
        log_step("Setting root password...")
        command = f"echo 'root:{password}' | chpasswd"
        if check_error(command, "Set root password") != 0:
            return False
        log_step("Root password set successfully.")

    # Step 5: Start SSH service
    log_step("Ensuring /run/sshd exists...")
    os.makedirs("/run/sshd", exist_ok=True)

    log_step("Starting SSH service...")
    if check_error('/usr/sbin/sshd', "Start SSH service") != 0:
        return False

    # Step 6: Verify SSH service is running
    log_step("Verifying SSH service status...")
    result = subprocess.run('pgrep -f /usr/sbin/sshd', shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        log_step("SSH service is running.")
        return True
    else:
        print("[ERROR] SSH service is not running.")
        return False
    def start_vscode(ws_dir=".", 
                 password="12345", 
                 vscode_dir='~/.vscode', 
                 install=False, 
                 extensions=["ms-python.python", 
                             "ms-toolsai.jupyter", 
                             "mechatroner.rainbow-csv", 
                             "vscode-icons-team.vscode-icons"]):
    print(f'{"*" * 10} SETUP VSCODE {"*"*10}')

    # vscode-server config
    extensions_dir = os.path.expanduser(f"{vscode_dir}/extensions")
    user_data_dir = os.path.expanduser(f"{vscode_dir}/user_data")

    def log_step(step):
        print(f"> {step}...")

    def check_error(command, step):
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] {step} failed. Error: {result.stderr.strip()}")
            return False
        print(f"[SUCCESS] {step} completed.")
        return True

    # Step 1: Create necessary directories
    log_step("Create necessary directories for vscode")
    os.makedirs(extensions_dir, exist_ok=True)
    os.makedirs(user_data_dir, exist_ok=True)
    print(f"[INFO] Directories created: {extensions_dir}, {user_data_dir}")

    # Step 2: Install code-server
    if install:
        log_step("Install code-server")
        if not check_error('curl -fsSL https://code-server.dev/install.sh | sh', "Install code-server"):
            return

    # Step 3: Run code-server
    log_step("Run code-server")
    if not check_error(f'sudo apt-get install -y screen && sudo screen -dmS vscode bash -c "PASSWORD={password} code-server --port 9000 --bind-addr 0.0.0.0 --user-data-dir={user_data_dir} --extensions-dir={extensions_dir} --disable-telemetry {ws_dir}"', "Run code-server"):
        return

    # Step 4: Install extensions
    log_step("Download and Install code-server extensions")
    for extension in extensions:
        log_step(f"Install extension: {extension}")
        if not check_error(f'code-server --install-extension {extension}', f"Install extension: {extension}"):
            return

    # Step 5: Check running screens
    log_step("Check running screen sessions")
    if not check_error('screen -wipe && screen -ls', "Check screen sessions"):
        return

    print(f'{"-" * 10} Finished {"-"*10}\n')
def start_ngrok(ngrok_tokens = [], 
                ngrok_binds  = {
                    'ssh': {'port':22, 'type':'tcp'}, 
                    'vscode': {'port':9000, 'type':'http'}
                }
               ):
    """
    start_ngrok:
    + ngrok_tokens: list of token getting from Authtoken in dashboard at https://ngrok.com
    + ngrok_binds : default: 
        {
            'ssh'   : {'port':22, 'type':'tcp'}, 
            'vscode': {'port':9000, 'type':'http'}
        }
    """
    def default_handler(ngrok, ngrok_info = {}):
        # bind with code-server: port 9000
        # vscode_tunnel = ngrok.connect(9000, "http")
        
        # bind with ports
        for name in ngrok_binds:
            try:
                tunnel = ngrok.connect(ngrok_binds[name].get('port', 80), 
                                   ngrok_binds[name].get('type', 'tcp'))
                ngrok_info[name] = tunnel
            except:
                print('failt')
            pass
        pass # default_handler
    
    print(f'{"*" * 10} SETUP NGROK {"*"*10}')
    try:
        from pyngrok import ngrok, conf
    except:
        # install pyngrok
        print(f'> Install ngrok...')
        get_ipython().system('pip install -qqq pyngrok 2>&1 > /dev/null')
        from pyngrok import ngrok, conf

    print(f'> Kill ngrok process...')
    get_ipython().system('kill -9 "$(pgrep ngrok)"')
    
    print(f'> Binding ports...')
    list_regions = ["us", "en", "au", "vn"]
    url, ssh_tunnel = None, None
    is_success = False
    ngrok_info = {}
    for auth_token in ngrok_tokens:
        if is_success: break
        for region in list_regions:  
            try:
                conf.get_default().region = region
                ngrok.set_auth_token(auth_token)

                default_handler(ngrok, ngrok_info)

                print("> Registry success!")
                is_success = True
                break
            except Exception as e:
                print(e)
                pass    
        # for

    for key in ngrok_info:
        print(f'{key}: {ngrok_info[key]}')
    
    print(f"")
    print(f'{"-" * 10} Finished {"-"*10}\n')
    pass 
