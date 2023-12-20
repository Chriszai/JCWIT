# JCWIT



# Description

JCWIT is a  correctness-witness validator used for validating result output by Java verifiers. It takes a Java program with safety properties and the corresponding correctness witnesses to validate the verification results. JCWIT extracts the invariants from the correctness witnesses and re-injects them as assertion statements into the original program using the Mockito framework. A Java model checker is used to re-verify these assertion statements to check whether they are hold in the original Java program. In addition, JCWIT determines the completeness of the correctness witnesses by checking for the existence of cycles.

# Architecture

**a. jcwit.py** - This file is the entry file and is responsible for parsing the input (witnesses), outputting the results and making calls to the relevant methods.

**b. validationharness.py** - This file is responsible for the construction of the validation harness and the insertion of the validation statements, and also includes the extraction of the types of non-determined variables from the original program.

**c. graphchecking.py** - This file is responsible for checking that the CFG in the correctness witness whether covers all the behaviour of the program.

**d. ValidationHarnessTemplate.txt** - This file is a template for the validation harness and will be converted to a validation harness after the template statements are inserted.

The following diagram depicts the software architecture of JCWIT.

![](C:\Users\MSI-PC\OneDrive\Pictures\JCWIT.jpg)

# Instructions

Specific steps on how to use JCWIT and the third-party libraries that need to be installed (mandatory) are listed below.

1. Start by obtaining JCWIT from Github with the given command:

   ```
   git clone https://github.com/Chriszai/JCWIT.git
   ```

2. Installing Python 3 is necessary for this project. Here you can find a installation instructions for setting up Python on several platforms
   https://realpython.com/installing-python/ or use the command given below:

   ```
   $ sudo apt-get update
   $ sudo apt-get install python
   ```

   If you want to install a specific version of Python, add the specific version after "Python", for example:

   ```
   $ sudo apt-get install python3.8
   ```

3. The additional third-party packages required by this Python script are as follows (mandatory):<br>
   • subprocess<br>
   • sys<br>
   • networkx<br>
   • random

   Please note that networkx needs to be installed separately; NetworkX requires Python 3.8, 3.9 or 3.10. Specific installation instructions are as follows. 

   https://www.osgeo.cn/networkx/install.html, Or you can simply install it with the Linux command:

   ```
   pip install networkx[default]
   ```

4.  JBMC supports multiple platforms including Ubantu, macOS, Windows and Docker. Different versions for different platforms can be found on the official GitHub. The GitHub link for JBMC is shown below:

   https://github.com/diffblue/cbmc/releases.

   On Ubuntu, install CBMC by downloading the *.deb package below for your version of Ubuntu and install with

   ```
   # Ubuntu 20:
   $ dpkg -i ubuntu-20.04-cbmc-5.95.1-Linux.deb
   ```

5. (Optional) JCWIT has already provided a complete library for the Mockito framework. The specific versions are as follows:

   | [byte-buddy-1.14.1.jar](https://github.com/Chriszai/JCWIT/blob/main/dependencies/byte-buddy-1.14.1.jar) |
   | ------------------------------------------------------------ |
   | [byte-buddy-agent-1.14.1.jar](https://github.com/Chriszai/JCWIT/blob/main/dependencies/byte-buddy-agent-1.14.1.jar) |
   | [mockito-core-5.2.0.jar](https://github.com/Chriszai/JCWIT/blob/main/dependencies/mockito-core-5.2.0.jar) |
   | [objenesis-3.3.jar](https://github.com/Chriszai/JCWIT/blob/main/dependencies/objenesis-3.3.jar) |

   If you want to use another version of the Mockito framework, Mockito is also available to download from the following site:
   https://mvnrepository.com/artifact/org.mockito/mockito-core.
   Please note that you must download the other three dependencies if you want to install them separately, or just import Mockito-core if you are using a tool such as IDEA to install via Maven. These mandatory dependencies are shown below: 

   • byte-buddy

   • byte-buddy-agent

   • objenesis

   • mockito-core

6. Next, use the following command to validate the selected Java file:

   ```
   ./jcwit.py --witness <path-to-witnesses>/*.graphml <path-to-java-files>/*.java
   ```

   where the parameter *.graphml indicates the witness to be validated, and *.java indicates a series of Java programs to be validated or all Java files in
   the directory of files to be validated.

   ```
   ./jcwit.py --version
   ```

​		This command is used to check the version of the script currently in use.

