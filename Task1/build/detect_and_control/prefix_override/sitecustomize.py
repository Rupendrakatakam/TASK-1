import sys
if sys.prefix == '/home/rupendra/Desktop/Tasks/Task1/task1-py310':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/rupendra/Desktop/Tasks/Task1/install/detect_and_control'
