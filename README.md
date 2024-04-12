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
- ChatGPT 4

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

### Using VM instead
Docker was limited in giving the full experience of installing gitlab. And the provided docker image for gitlab doesn't support Windows Docker. So instead create a VM for linux to go forward.

#### Install
- Install VirtualBox.
- Download RockyLinux latest version 9. DVD .iso

Problem: When starting up VM it gave glitched out graphics.  
Solution: Allocate >128MB graphics memory. And when starting VM, press F12 to go into boot select mode, and manually select the .iso file.

#### General
- Click on VM to give keyboard and mouse control to VM. Press 'host key', default right ctrl, to get out of the VM.
- Best security practices: 
   - Lock root account. Only use less-privileged users that can use 'sudo' to do more privileged actions (extra step + logging).
   - Dissallow ssh root access with password, as it allows brute forcing the password.
   - Enable KDUMP for when the kernel fails.
   - Choose security profile CIS intermediate (or basis/advanced. It's a trade-off between security and usability).

Options: Server with GUI.  
No addiontal software for now.