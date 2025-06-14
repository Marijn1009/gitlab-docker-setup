# Gitlab-docker-setup

## Goal

1. Setup a Linux server using Docker
   - Use proper user management
2. Setup self-managed GitLab
3. Deploy Git hooks in Python to set rules for commits

Techniques: Docker, Git, GitLab, Linux, Python, Git Bash, VScode. 

## Documentation

- [Docker guide](https://docs.docker.com/get-started/overview/)
- [CentOS guide](https://www.geeksforgeeks.org/getting-started-with-centos/)
- [Gitlab installation on linux](https://docs.gitlab.com/omnibus/installation/index.html)

## Pre-installations

Install on windows pc:
- Docker Desktop
- Git (including git bash)
- VSCode

## Commands Used

| Type    | Command                                            | Description |
|---------|----------------------------------------------------|-------------|
| Docker  | `docker pull image-name`                           | Get the image from Docker Hub. Can use tags for specific versions. |
| Docker  | `winpty docker run -it --name my-container-name -p 8000:8000 image-name` | Run the image in a container. `winpty` is used for compatibility with Windows terminals. `-it` makes the container interactive and allocates a pseudo-TTY. `--name my-container-name` names the container for easier reference. `-p 8000:8000` maps port 8000 on the host to port 8000 on the container. |
| Docker  | `docker ps -a`                                     | List containers. Default doesn't show stopped containers, while '-a' shows all. |
| Docker  | `docker start my-container-name`                   | Start a specific container. |
| Docker  | `docker exec -it my-container-name bash`           | Execute commands in a running container. Here, it starts a bash shell in the container. |
| VSCode  | `code .`                                           | Open the current directory in Visual Studio Code. Useful for editing files or managing projects within VSCode. |
| Git     | `git add .`                                        | Add all changes in the current directory to the staging area. |
| Git     | `git commit -m "commit message"`                   | Commit the staged changes with a descriptive message. |
| Git     | `git remote add origin https://github.com/username/repository.git` | Link your local repository to a remote GitHub repository. |
| Git     | `git push -u origin master`                        | Push the committed changes to the master branch on GitHub. For the first push, '-u' sets the upstream branch. |
| Git     | `git push`                                         | Push the committed changes to the linked remote repository. Used after the initial push. |


## Docker
Follow docker get started guide to get used to commands.

Then figure out which linux image to use. I want CentOS or similar, because it is commonly used in companies. 
- CentOS 7 & 8 are soon no longer supported. Stream 8 and 9 are supported, but don't have an official docker image. 
- Rocky Linux is good! Gives the exact same experience. "Rocky Linux is a community enterprise operating system designed to be 100% bug-for-bug compatible with RHEL. It was created in response to CentOS's shift from a stable server distribution to a rolling release."

#### Start the container

In Git Bash:

```bash
docker pull rockylinux/rockylinux

winpty docker run -it --name my-rockylinux -p 8000:8000 rockylinux/rockylinux
```
Now the rockylinux terminal opens. Linux is ready to use and experiment with. 

#### Setup user management

This can also be done in a dockerfile.

```bash
dnf -y install sudo
adduser mverhaeg
echo "mverhaeg ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
su mverhaeg
```

#### Setup self-managed Gitlab

Follow [documentation](https://about.gitlab.com/install/#almalinux).

```bash
sudo dnf install -y curl policycoreutils openssh-server perl

```

Skip the systemctl steps as Docker doesn't support them by default. Not necessary to setup network access for now. 

```bash
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.rpm.sh | sudo bash
sudo EXTERNAL_URL="http://gitlab.mverhaeg.com" dnf install -y gitlab-ce
```

Install top to see if installation is stuck:

```bash
# Install top
sudo dnf -y install procps-ng
top

# Install htop
sudo dnf install -y epel-release
sudo dnf install -y htop
htop
```

## Using VM instead
Docker was limited in giving the full experience of installing gitlab. And the provided docker image for gitlab doesn't support Windows Docker. So instead create a VM for linux to go forward.

#### Install
- Install VirtualBox.
- Download RockyLinux latest version 9. DVD .iso

Problem: When starting up VM it gave glitched out graphics.  
Solution: Allocate >128MB graphics memory. And when starting VM, press F12 to go into boot select mode, and manually select the .iso file.

#### General
- Click on VM to give keyboard and mouse control to VM. Press 'host key', default right ctrl, to get out of the VM.
- Fullscreen: Host + F
- Best security practices: 
   - Lock root account. Only use less-privileged users that can use 'sudo' to do more privileged actions (extra step + logging).
   - Dissallow ssh root access with password, as it allows brute forcing the password.
   - Enable KDUMP for when the kernel fails.
   - Choose security profile CIS intermediate (or basis/advanced. It's a trade-off between security and usability).

Options: Server with GUI.  
No addiontal software for now.

#### Install Guest Additions 
This gives  multiple quality of life upgrades, including correct scaling. Select Devices > Insert Guest Additions CD image. 

If there is an error about missing kernel headers, run commands:
```
sudo dnf install epel-release
sudo dnf update
sudo dnf install kernel-devel kernel-headers gcc make perl
cd /run/media/$(whoami)/VBOX_GUEST_ADDITIONS
sudo ./VBoxLinuxAdditions.run
```

Now select view > Auto-resize guest display. 
And select Devices > Shared clip-board > Bidirectional


### Gitlab install on VM
Follow [gitlab install](https://about.gitlab.com/install/#almalinux) for ArmaLinux (RHEL 9 combatible).

Setup DNS:
- Find ip ```ip addr show```
- Add DNS entry: ```vim /etc/hosts``` add line such as ```0.0.0.0 gitlab.local```

Reset password according to [here](https://docs.gitlab.com/ee/security/reset_user_password.html). 
Create new account on login page. Login as root to approve account.

Any time you shutdown the VM and want to start gitlab again: ```sudo gitlab-ctl restart```.

## Setup Hooks
See [GitLab Documentation](https://docs.gitlab.com/ee/administration/server_hooks.html).

See pre-receive-hook.py, this is the hook we want to run. It checks every filename within the commit for whitespace.

```
mkdir -p custom_hooks/pre-receive.d
touch custom_hooks/pre-receive.d/pre-receive.py
vim custom_hooks/pre-receive.d/pre-receive.py
chmod +x custom_hooks/pre-receive.d/pre-receive.py
tar -cf custom_hooks.tar custom_hooks
```

Create a custom_hooks/pre-receive.d/pre-receive.py with the python code. Create tar ```tar -cf custom_hooks.tar custom_hooks```.

Finding storage and path (first command takes long):
```
sudo gitlab-rails console
project = Project.find_by_full_path('mverhaeg/test-project')
puts project.repository_storage
puts project.disk_path
```

Set the hook:
```
cat custom_hooks.tar | sudo /opt/gitlab/embedded/bin/gitaly hooks set --storage default --repository @hashed/6b/86/6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b.git --config /var/opt/gitlab/gitaly/config.toml
```

### Global hook
When having many repositories, it is possible to use a global hook that is immediately active for all repositories.

- In gitlab settings ```gitlab.rb```, choose server hook directory.  
```
sudo vim /etc/gitlab/gitlab.rb # search for 'custom_hooks_dir'. Uncomment the starting 'gitaly['configuration'] = {' line, the 'hooks: { ... }' lines, and the final '}' line
```
Now reconfigure and restart:
"Reconfiguring GitLab should occur in the event that something in its configuration (/etc/gitlab/gitlab.rb) has changed."
```
sudo gitlab-ctl reconfigure
sudo gitlab-ctl restart
```

Create the hook in ```sudo -i``` session (no restart needed):  
```
cd /var/opt/gitlab/gitaly
mkdir -p custom_hooks/pre-receive.d
touch custom_hooks/pre-receive.d/pre-receive.py
vim custom_hooks/pre-receive.d/pre-receive.py # copy pre-receive-hook.py into it
chmod +x custom_hooks/pre-receive.d/pre-receive.py
chown git:git custom_hooks/pre-receive.d/pre-receive.py
```

### Test if it works
Make commit without whitespace in titles. It should work as normal. Now make commit with whitespace which should give an error.

And to fix it, just rename the file to not have whitespace and then commit it. The new commit with fixed filenames does work!

### Troubleshooting
Setting up git and keys on linux to test directly in VM:
- sudo dnf install git
- Make directory ~/.ssh and files id_rsa and id_rsa.pub. Use chmod 600 to set permissions right.
- Start key agent with ```eval "$(ssh-agent -s)"``` and add key ```ssh-add ~/.ssh/id_rsa```
- Clone project: ```git clone git@gitlab.local:mverhaeg/test-project.git```

