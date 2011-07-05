#!/usr/bin/env python
"""
SERVER CONTROL SCRIPT

Sets the appropriate environmental variables and launches the server
process. Run the script with the -h flag to see usage information.
"""
import os  
import sys
import signal
from optparse import OptionParser
from subprocess import Popen, call

import settings

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                     
# Name of the twistd binary to run
TWISTED_BINARY = 'twistd' 
# The .py file twistd will run.
SERVER_PY_FILE = os.path.join(settings.SRC_DIR, 'server/server.py')

# Add this to the environmental variable for the 'twistd' command.
thispath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if 'PYTHONPATH' in os.environ:
    os.environ['PYTHONPATH'] += (":%s" % thispath)
else:
    os.environ['PYTHONPATH'] = thispath

def get_server_log_filename():
    """
    Returns the server's standard log filename.
    """
    return os.path.join(settings.LOG_DIR.strip(), 'server.log')

def cycle_logfile():
    """
    Move the old log file to server.log.old (by default).

    """    
    logfile = get_server_log_filename()
    logfile_old = logfile + '.old'
    if os.path.exists(logfile):
        # Cycle the old logfiles to *.old
        if os.path.exists(logfile_old):
            # E.g. Windows don't support rename-replace
            os.remove(logfile_old)
        os.rename(logfile, logfile_old)

def start_daemon(parser, options, args):
    """
    Start the server in daemon mode. This means that all logging output will
    be directed to logs/server.log by default, and the process will be
    backgrounded.
    """ 
    if os.path.exists('twistd.pid'):
        print "A twistd.pid file exists in the current directory, which suggests that the server is already running."
        sys.exit()
    
    print '\nStarting %s server in daemon mode ...' % settings.GAME_NAME
    print 'Logging to: %s.' % get_server_log_filename()
    
    # Move the old server.log file out of the way.
    #cycle_logfile()

    # Start it up
    Popen([TWISTED_BINARY, 
           '--logfile=%s' % get_server_log_filename(), 
           '--python=%s' % SERVER_PY_FILE])

def start_interactive(parser, options, args):
    """
    Start in interactive mode, which means the process is foregrounded and
    all logging output is directed to stdout.
    """
    print '\nStarting %s server in interactive mode (stop with keyboard interrupt) ...' % settings.GAME_NAME
    print 'Logging to: Standard output.'

    try:
        call([TWISTED_BINARY, 
              '-n', 
              '--python=%s' % SERVER_PY_FILE])
    except KeyboardInterrupt:
        pass

def stop_server(parser, options, args):
    """
    Gracefully stop the server process.
    """
    if os.name == 'posix': 
        if os.path.exists('twistd.pid'):
            print 'Stopping the %s server...' % settings.GAME_NAME
            f = open('twistd.pid', 'r')
            pid = f.read()
            os.kill(int(pid), signal.SIGINT)
            print 'Server stopped.'
        else:
            print "No twistd.pid file exists, the server doesn't appear to be running."
    elif os.name == 'nt':
        print '\n\rStopping cannot be done safely under this operating system.' 
        print 'Kill server using the task manager or shut it down from inside the game.'
    else:
        print '\n\rUnknown OS detected, can not stop. '
        

def main():
    """
    Beginning of the program logic.
    """
    parser = OptionParser(usage="%prog [options] <start|stop>",
                          description="This command starts or stops the %s game server. Note that you have to setup the database by running  'manage.py syncdb' before starting the server for the first time." % settings.GAME_NAME)
    parser.add_option('-i', '--interactive', action='store_true', 
                      dest='interactive', default=False,
                      help='Start in interactive mode')
    parser.add_option('-d', '--daemon', action='store_false', 
                      dest='interactive',
                      help='Start in daemon mode (default)')
    (options, args) = parser.parse_args()
    
    if "start" in args:
        if options.interactive:
            start_interactive(parser, options, args)
        else:
            start_daemon(parser, options, args)
    elif "stop" in args:
        stop_server(parser, options, args)
    else:
        parser.print_help()
if __name__ == '__main__':
    main()
