import os
import getpass
import pwd

# Curtosy of: https://unix.stackexchange.com/questions/11470/how-to-get-the
# -name-of-the-user-that-launched-sudo

def getSudoingUser():

    # This is the generic method. First thing to try.
    try:
        return os.getlogin()
    except OSError:
        # failed in some ubuntu installations and in systemd services
        pass

    # If the above method fails try to obtain the environmental
    # variable.
    try:
        user = os.environ['USER']
    except KeyError:
        # possibly a systemd service. no sudo was used
        return getpass.getuser()

    # This should only happend, if sudo was called without -u.
    # Don't allow this in /etc/sudoers.
    if user == 'root':
        try:
            return os.environ['SUDO_USER']
        except KeyError:
            # no sudo was used
            pass

        try:
            pkexec_uid = int(os.environ['PKEXEC_UID'])
            return pwd.getpwuid(pkexec_uid).pw_name
        except KeyError:
            # no pkexec was used
            pass

    return user
