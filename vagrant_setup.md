

## Step 1: Install Vagrant and VirtualBox

1. Go to [Vagrant downloads](http://www.vagrantup.com/downloads) and download the **Windows installer**. Install it.
2. Go to [VirtualBox downloads](http://www.virtualbox.org/) and download the **Windows installer**. Install it.
3. Restart your computer after installation (to make sure both tools are recognized in PATH).

---

## Step 2: Create a Folder for Your VM

1. Open **Windows Terminal** (or Command Prompt / PowerShell).
2. Choose a folder where you want to store your VM files. For example, on your desktop:

   ```powershell
   cd Desktop
   mkdir validate_email_vm
   cd validate_email_vm
   ```

---

## Step 3: Initialize and Start the Vagrant VM

1. Initialize a basic Linux VM (Ubuntu 32-bit) in this folder:

   ```bash
   vagrant init hashicorp/precise32
   ```
2. Start the VM:

   ```bash
   vagrant up
   ```

   * This downloads the VM box and boots it.
3. SSH into the VM:

   ```bash
   vagrant ssh
   ```

   * You are now inside the Linux VM. All further commands are **inside the VM**, not your Windows PC.

---

## Step 4: Install Python and pip inside the VM

1. Update your VM packages:

   ```bash
   sudo apt-get update
   ```
2. Install Python and pip:

   ```bash
   sudo apt-get install python python-pip -y
   ```
3. Verify pip is installed:

   ```bash
   pip --version
   ```

---

## Step 5: Install `pyDNS` (Dependency for validate_email)

1. Install pyDNS:

   ```bash
   sudo pip install pydns
   ```
2. Confirm it installed successfully:

   ```bash
   python -c "import DNS; print('pyDNS installed')"
   ```

---

## Step 6: Install Git

1. Install git:

   ```bash
   sudo apt-get install git -y
   ```
2. Check it:

   ```bash
   git --version
   ```

---

## Step 7: Clone the `validate_email` Repository

1. Inside the VM, clone the repo using HTTPS (safer for beginners):

   ```bash
   git clone https://github.com/efagerberg/validate_email.git
   ```
2. Go into the project folder:

   ```bash
   cd validate_email
   ```

> ⚠ Optional: If you want to use your Windows SSH keys, you need to enable agent forwarding in the `Vagrantfile` by adding:
>
> ```ruby
> Vagrant.configure("2") do |config|
>   config.ssh.forward_agent = true
> end
> ```
>
> Then run `vagrant reload` to apply changes.

---

## Step 8: Run `validate_email.py`

1. Make sure you are inside the `validate_email` folder:

   ```bash
   pwd
   ```

   * Should show something like `/home/vagrant/validate_email`
2. Run the script:

   ```bash
   python validate_email.py
   ```
3. Follow any prompts or instructions the script gives.

---

✅ At this point, `validate_email` should be installed and ready to use inside your VM. You don’t need to touch Windows beyond launching the VM.

---
