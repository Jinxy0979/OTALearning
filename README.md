# OTALearning

A prototype on learning one-clock timed automata.

### Overview

This tool is dedicated to learning deterministic one-clock timed automata (DOTAs) which is a subclass of timed automata with only one clock. In 1987, Dana Angluin introduced the L* Algorithm for learning regular sets from queries and counterexamples. The tool implement an Angluin-style active learning algorithm on DOTAs. This branch is the smart teacher situation with an accelerating trick. The `dev` branch is the version without the accelerating trick. The `normal` branch is about the normal teacher situation.

### Installation & Usage

#### Prerequisite

- Python 3.5.* (or high)


#### Installation

- Just download.

It's a pure Python program.  We have test it on Ubuntu 16.04 64bit with Python 3.5.2.

#### Usage

For example

```shell
python3 learnota.py experiments/example.json
```

- `learnota.py` is the main file of the program.

- The target DOTA is stored in a JSON file, in this example, `example.json` . The details are as follows.

  ```json
  {
    "name": "A",
    "l": ["1", "2"],
    "sigma": ["a", "b"],
    "tran": {
  	    "0": ["1", "a", "(1,3)", "n", "2"],
  	    "1": ["1", "b", "[0,+)", "r", "1"],
  	    "2": ["2", "b", "[2,4)", "r" "2"]
    },
    "init": "1",
    "accept": ["2"]
  }
  ```

  - "name" : the name of the target DOTA;
  - "l" : the set of the name of locations;
  - "sigma" : the alphabet;
  - "tran" : the set of transitions in the following form:
    - transition id : [name of the source location, action, guard, reset, name of the target location];
    - "+" in a guard means INFTY​;
    - "r" means resetting the clock, "n" otherwise.

  - "init" : the name of initial location;
  - "accept" : the set of the name of accepting locations.

#### Output

- Every iteration instance of the timed observation table during the learning process;
- If we learn the target DOTA successfully, then the finial COTA will be printed on the terminal. Additionally, the total time, the size of S​, the size of ​R​, the size of ​E​, the number of equivalence query, and the number of membership query will also be given. 
- The randomly experiments can be conducted by running the shell scripts in the corresponding folders. The results are stored in a folder named "result". In a result file,  one line for  a DOTA. The 8 numbers mean the total time, |S|,|R|,|E|(excluding the empty word), the iteration numbers of the table, the number of membership queries, the number of equivalence queries and the number of locations in the learned DOTA, respectively. (Running them in the usual way is also ok, but it will not record the result in a file.)
