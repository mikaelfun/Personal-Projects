# Enter your code here. Read input from STDIN. Print output to STDOUT
import sys
import os
import threading
from collections import Counter


class myThread(threading.Thread):
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.threadID = id
        self.result = {}
        self.filesProcessed = 0

    def processFile(self, dic, curFile):
        f = open(DirectoryWordFrequencyCounter.filePath + '\\'+curFile, 'r')
        for line in f:
            for word in line.split():
                if word in dic:
                    dic[word] += 1
                else:
                    dic[word] = 1

    def myWorker(self):
        dic = {}
        while True:
            DirectoryWordFrequencyCounter.lock.acquire()
            if DirectoryWordFrequencyCounter.left == 0:
                DirectoryWordFrequencyCounter.lock.release()
                # finish this thread
                # print ("Thread ", self.threadID, "Thread out")
                return dic
            else:
                curFile = DirectoryWordFrequencyCounter.left - 1
                DirectoryWordFrequencyCounter.left -= 1
                DirectoryWordFrequencyCounter.lock.release()
                self.processFile(dic, DirectoryWordFrequencyCounter.filelist[curFile])
                self.filesProcessed += 1

    def run(self):
        print ("Thread ", self.threadID, "Thread enter")
        self.result = self.myWorker()
        print ("Thread ", self.threadID, "files processed: ", self.filesProcessed)
        print ("Thread ", self.threadID, "Thread out")

    def getResult(self):
        # print ("Thread ", self.threadID, "results: ", self.result)
        # print ("Thread ", self.threadID, "files processed: ", self.filesProcessed)
        return self.result


class DirectoryWordFrequencyCounter:
    num = 0
    left = 0
    lock = None
    filelist = []
    def __init__(self, filePath):
        DirectoryWordFrequencyCounter.filelist = os.listdir(filePath)
        DirectoryWordFrequencyCounter.num = len(self.filelist)
        DirectoryWordFrequencyCounter.left = DirectoryWordFrequencyCounter.num
        DirectoryWordFrequencyCounter.lock = threading.Lock()
        DirectoryWordFrequencyCounter.filePath = filePath


    def sumALl(self, dics):
        out = {}
        for each in dics:
            out = dict(Counter(each) + Counter(out))
        return out

    def countMultithreaded(self):
        myThreads = []
        for i in range(20): # 20 threads since 10 cores
            myThreads.append(myThread(i))
        for eachThread in myThreads:
            eachThread.start()
        for eachThread in myThreads:
            eachThread.join()
        results = []
        for eachThread in myThreads:
            results.append(eachThread.getResult())
        myResult = self.sumALl(results)
        # print (myResult)
        return myResult

if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     sys.exit()
    # filePath = sys.argv[1]
    filePath = "pos"
    myCounter = DirectoryWordFrequencyCounter(filePath)
    myCounter.countMultithreaded()
