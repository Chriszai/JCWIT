# JCWIT



# Description

JCWIT is a  correctness-witness validator used for validating result output by Java verifiers. It takes a Java program with safety properties and the corresponding correctness witnesses to validate the verification results. JCWIT extracts the invariants from the correctness witnesses and re-injects them as assertion statements into the original program using the Mockito framework. A Java model checker is used to re-verify these assertion statements to check whether they are hold in the original Java program. In addition, JCWIT determines the completeness of the correctness witnesses by checking for the existence of cycles.

# Architecture

**a. jcwit.py** - This file is the entry file and is responsible for parsing the input (witnesses), outputting the results and making calls to the relevant methods.

**b. validationharness.py** - This file is responsible for the construction of the validation harness and the insertion of the validation statements, and also includes the extraction of the types of non-determined variables from the original program.

**c. graphchecking.py** - This file is responsible for checking that the CFG in the correctness witness whether covers all the behaviour of the program.

**d. ValidationHarnessTemplate.txt** - This file is a template for the validation harness and will be converted to a validation harness after the template statements are inserted.

Installing Python 3 is necessary for this project. Here you can find a installation instructions for setting up Python on several platforms:
https://realpython.com/installing-python/

The additional third-party packages required by this Python script are as follows (mandatory):<br>
• subprocess<br>
• sys<br>
• networkx<br>
• random

JBMC supports multiple platforms including Ubantu, macOS, Windows and Docker. Different versions for different platforms can be found on the official GitHub. Belowis anexample for Windows only. The GitHub link for JBMC is shown below:
https://github.com/diffblue/cbmc/releases.

Mockito is available to download from the following site:
https://mvnrepository.com/artifact/org.mockito/mockito-core
If you want to use Mockito successfully, you need to download the other three
dependencies separately, or just import Mockito-core if you are using a tool such as IDEAto install it via Maven. These dependencies are shown below: 
• byte-buddy
• byte-buddy-agent
• objenesis

Next, run the script with the benchmark using the following command:

**./jcwit.py --witness [witness_file] [list of folders/JavaFiles]**

OR

**./jcwit.py --version**

The first line of the command will validate the input file, which can be either a .java or a .class file, and the script will automatically convert the file format to .class internally. 
The second command is used to check the version of the script currently in use.