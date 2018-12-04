"""
ID 27799964
FIT2004 Assignment 3
"""

import itertools

# Constants
INDEX = 1 - ord('a')
score_file = open("Scores.txt")
score_list = [0 for x in range(27)]
for line in score_file:
    line = line.strip()
    line = line.split(":")
    score_list[ord(line[0]) - 96] = int(line[1])


def get_letter_score(char):
    return score_list[ord(char) - 96]

def get_word_score(aStr, letterNum, boostAmount):
    score = 0
    for i in range(len(aStr)):
        char = aStr[i]
        if i == letterNum:
            score += get_letter_score(char) * boostAmount
        else:
            score += get_letter_score(char)
    return score


def insertionSort(aList):
    for i in range(1,len(aList)):
        key = aList[i]
        j = i - 1
        while j >= 0 and key[1] < aList[j][1]:
            aList[j+1] = aList[j]
            j -= 1
        aList[j+1] = key
    return aList


def sortWord(word):
    """Sorts the letters in a word in alphabetical order using counting sort.
    Args:
        word (str): must consist of only alphabetical characters.
    Returns:
        output (str): letters of input word sorted in alphabetical order.
    Time complexity:
        Worst case O(k) where k is the length of the input word
    Space complexity:
        Worst case O(k)
    """
    m = len(word)
    count = [0] * 26
    output = ''
    for i in range(m):
        count[ord(word[i]) - 97] += 1
    for j in range(26):
        for k in range(count[j]):
            output += chr(j + 97)
    return output


class Trie:
    """
    Trie where each node corresponds to a character in the alphabet. Array implementation.
    """

    def __init__(self, wordList):
        self.root = TrieNode('*')
        self.count = 0  # We don't count the root node
        self.wordList = wordList
        self.largestIndices = []

    def isEmpty(self):
        return self.count == 0

    def insertAll(self):
        """
        Inserts all indices into the Trie. Keep track of the anagram with the highest letter score at each column.
        """
        maxLength = 0
        maxAnagrams = []  # Pointer to largest list of anagrams

        for index in range(len(self.wordList)): # Iterate through all words
            originalWord = self.wordList[index]
            word = self.wordList[index]
            word = sortWord(word)
            word = word + '$'
            current = self.root

            for i in range(len(word)):  # Iterate through characters (c) in word
                c = word[i]
                # Check if we have reached the last character
                if c == '$':
                    if current.children[0] != -1:  # If anagram already in list
                        current.children[0].append(originalWord)  # Add it to last node
                    else:  # If anagram not in list
                        current.children[0] = leafNode()  # Create a new leaf node
                        current.children[0].append(originalWord)  # Add current index at end of leaf node
                        # Set bestWordColumn to 0 appropriately
                        current.children[0].bestWordColumn = [0] * len(originalWord)
                    if len(current.children[0]) > maxLength:  # Update longest anagrams if necessary
                        maxLength = len(current.children[0])
                        maxAnagrams = current.children[0].anagrams
                    break

                # Check if c is a child of current node
                elif current.children[ord(c) + INDEX] != -1:
                    current = current.children[ord(c) + INDEX]  # Move to node containing c

                # If a node with the child does not exist as a child of the current node, create it.
                else:
                    current.children[ord(c) + INDEX] = TrieNode(c)
                    current = current.children[ord(c) + INDEX]

            # update
            current.children[0].updateBestColumn()

        # Set largest anagram
        self.largestAnagrams = maxAnagrams

    def getLargestAnagram(self):
        """
        Returns the largest group of anagrams in the input dictionary.
        """
        return self.largestAnagrams

    def findWords(self, query):
        """
        Returns all words that can be made using all letters in the query string.
        """
        query = sortWord(query)
        query += '$'
        current = self.root
        for c in query:
            if c == '$':
                if current.children[0] != -1:
                    output = current.children[0].anagrams
                else:
                    return []
            elif current.children[ord(c) + INDEX] != -1:  # Check if a node containing c exists
                current = current.children[ord(c) + INDEX]
            else:
                return []
        return output

    def getBestAnagram(self, aStr, letterNum):
        if len(aStr) <= letterNum:
            return aStr
        aStr = sortWord(aStr)
        node = self.getNode(aStr)
        if node:
            index = node.bestWordColumn[letterNum]
            return node.anagrams[index]
        return None

    def getNode(self, query):
        """
        Return the node that corresponds to the query string (if it exists)
        """
        query = sortWord(query)
        query += '$'
        current = self.root
        for c in query:
            if c == '$':
                if current.children[0] != -1:
                    output = current.children[0]
                else:
                    return []
            elif current.children[ord(c) + INDEX] != -1:  # Check if a node containing c exists
                current = current.children[ord(c) + INDEX]
            else:
                return []
        return output

    def getHighestCandidate(self, query, letterNum, boostAmount):
        """
        For task 3
        """
        letterNum = letterNum - 1
        # Generate all permutations of the query string O(2^k * k)
        n = len(query)
        binaryList = [list(i) for i in itertools.product([0, 1], repeat=n)]
        strList = []

        for i in range(len(binaryList)):            # Iterate through binaryList
            currentStr = ""
            for j in range(len(binaryList[i])):     # Iterate through numbers in binaryList[i]
                if binaryList[i][j] == 1:
                    currentStr += query[j]
            if currentStr != "":
                bestAnagram = self.getBestAnagram(currentStr, letterNum)
                if bestAnagram is not None:
                    currentScore = get_word_score(bestAnagram, letterNum, boostAmount)
                    strList.append([currentStr, currentScore])

        # Sort by score O(N)
        strList = insertionSort(strList)

        # If same score, put lexicographically smallest last
        for i in range(len(strList)-1):
            if ord(strList[i][0][0]) < ord(strList[i+1][0][0]):
                strList[i], strList[i+1] = strList[i+1], strList[i]

        # Search for the one(s) with the max score in the Trie
        # Return the word with the best score for the given letterNum (column).
        candidates = []

        for i in range((len(strList) - 1), -1, -1):
            currentItem = strList[i][0]
            candidates = self.findWords(currentItem)
            if candidates:
                break
        if candidates == []:
            return ['n/a', 0]

        # Find the word with the best score for the given letterNum (column).
        node = self.getNode(currentItem)
        index = node.bestWordColumn[letterNum]
        outputStr = node.anagrams[index]
        outputScore = get_word_score(outputStr, letterNum, boostAmount)
        return [outputStr, outputScore]

class TrieNode:
    """
    Node of a trie containing its value and a reference to its children. The children are stored in an array containing
    other instances of the TrieNode class.
    """

    def __init__(self, value):
        self.value = value
        self.children = [-1] * 27  # Array of length 27 (all letters plus $) to store children

    def __str__(self):
        return str(self.value)


class leafNode:
    """
    If the value is $, then it leads to a leaf that contains the index of the word we just inserted.
    """

    def __init__(self):
        self.anagrams = []
        self.bestWordColumn = []

    def append(self, index):
        self.anagrams.append(index)

    def __len__(self):
        return len(self.anagrams)

    def __str__(self):
        output = ""
        for word in self.anagrams:
            output += (word + ", ")
        output.strip(",")
        return output

    def updateBestColumn(self):
        word = self.anagrams[-1]
        for i in range(len(word)):
            letter = word[i]
            score = get_letter_score(letter)
            max_letter = self.anagrams[self.bestWordColumn[i]][i]
            max_score = get_letter_score(max_letter)
            if score > max_score:
                self.bestWordColumn[i] = len(self)-1


"""
Create the anagram trie and import all words in it. This is in the global window so it can be accessed by all functions. 
"""
wordFile = open("Dictionary.txt")
wordList = []
for word in wordFile:
    word = word.strip('\n')
    wordList.append(word)

a_trie = Trie(wordList)
a_trie.insertAll()


def solve_task1():
    # Returns a list corresponding to the largest group of anagrams in sorted order.
    return a_trie.getLargestAnagram()


def solve_task2(query):
    # implement your solution for task 2 inside this function. 
    # this function must return all words that can be made using all letters of the query (in sorted order)
    # feel free to create as many other functions as needed
    return a_trie.findWords(query)


def solve_task3(query, letter_num, boost_amount):
    # implement your solution for task 3 inside this function. 
    # this function must return a list containing two values [bestWord, score] where bestWord is the best possible word and score is its score
    return a_trie.getHighestCandidate(query, letter_num, boost_amount)


#############################################################################
# WARNING: DO NOT MODIFY ANYTHING BELOW THIS.
# PENALTIES APPLY IF YOU CHANGE ANYTHING AND TESTER FAILS TO MATCH THE OUTPUT
#############################################################################

# this function returns the score of a given letter
def get_letter_score(char):
    return score_list[ord(char) - 96]


def print_task1(aList):
    string = ", ".join(aList)
    print("\nThe largest group of anagrams:", string)


def print_task2(query, aList):
    string = ", ".join(aList)

    print("\nWords using all letters in the query (" + query + "):", string)


def print_task3(query, score_boost, aList):
    if len(aList) == 0:
        print("\nThe best word for query (" + query + "," + score_boost + "):",
              "List is empty, task not attempted yet?")
    else:
        print("\nThe best word for query (" + query + "," + score_boost + "):", str(aList[0]) + ", " + str(aList[1]))


def print_query(query, score_boost):
    unique_letters = ''.join(set(query))
    unique_letters = sorted(unique_letters)
    scores = []
    for letter in unique_letters:
        scores.append(letter + ":" + str(get_letter_score(letter)))
    print("Scores of letters in query: ", ", ".join(scores))


# score_list is an array where the score of a is at index 1, b at index 2 and so on
score_file = open("Scores.txt")
score_list = [0 for x in range(27)]
for line in score_file:
    line = line.strip()
    line = line.split(":")
    score_list[ord(line[0]) - 96] = int(line[1])

anagrams_list = solve_task1()
print_task1(anagrams_list)

query = input("\nEnter the query string: ")

while query != "***":
    score_boost = input("\nEnter the score boost: ")
    print_query(query, score_boost)

    score_boost_list = score_boost.split(":")
    letter_num = int(score_boost_list[0])
    boost_amount = int(score_boost_list[1])

    results = solve_task2(query)
    print_task2(query, results)

    answer = solve_task3(query, letter_num, boost_amount)
    print_task3(query, score_boost, answer)

    query = input("\nEnter the query string: ")

print("See ya!")
