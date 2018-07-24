/*
Author: Kun Fang (mikael8fun@gmail.com)


AppGuard Code Challenge:
Write a multithreaded program that:
1. Generates N random integers between 0-9
2. Counts how many times each integer was repeated
The program shall use:
1. A queue of max 10 elements to store the integers
2. A tracking array of exactly 10 elements to store the repetition counts. The array index
correspond to the numbers 0-9.
What you need to do:
- Use C/C++ language.
- Create 4 threads.
- Threads #1 and #2 generate a total of N random integers between 0-9 and put them into
a queue with a maximum size of 10 elements. If queue is full - the threads wait.
- Threads #3 and #4 read from the queue and increment the array value at the
corresponding index. If the queue is empty - the threads wait.
- When all N numbers are generated and counted, the threads must exit gracefully and
the program then outputs the resulting tracking array.
- You may use any editor/compiler of your choice. We prefer if Visual Studio is used but
anything that gets the job done is acceptable.
What
*/

#include <thread>         
#include <chrono>         
#include <iostream>
#include <future>
#include <vector>
#include <queue>
#include <string>
#include <time.h>
#include <mutex>
#include <conio.h>
#include <condition_variable>
using namespace std;

int PROCESS_LOG = 0;  // global log switch
					  /*
    Some difficulties while developing the solution:
    1. Came to condition_variable deadlocks and stuck for so long
    a) Especially for this case where there are multithreads for the same function
    b) Don't know whom and when to notify the condition variables
    c) Base case conditions unclear, don't know where to define
    
    Some solutions that I gradually come up with:
    a) The outer while loop judges the base case
    b) After wait function is called, it should also judge the base case
    since the status might have changed by other thread doing the same task
    c) Whenever reaches a base case(no integers to create, no elements to pop from queue),
    just notify all other threads. It doesn't harm to notify_all, I could be wrong..
    d) Debugging a multithreaded program is hard. Since the behavior is uncertain.
    Sometimes it ends up with a deadlock and sometimes it is just fine.
    Need excessive logical thinking while developing this kind of program
    e) By printing out each thread ID and corresponding current status, it
    helps a lot to understand what the machine is undergoing and where it
    could possibly cause the deadlock.
    2. Don't know how use Visual Studio's debugging tools
    ...Just use more often, practice makes perfect
    3. Tried to use srand(time(NULL)) but it makes random numbers biased.
    Skipped srand(), results are more evenly distributed
    
    
    Change log:
    1. Removed debug_log
    2. Added a mutex called mtx_cout to resolve cout race condition between thread
    group 1&2 and thread group 3&4 (thread 1 & 2 will not be racing for cout since
    they are protected by mtx_insert, thread 3 & 4 will also not be racing for cout
    since they are prtected by mtx_popback, but thread 1 and thread 3 could be using
    cout at the same time so there needs protection)
    3. Fixed a bug that the thread function does not notify other threads when exited
    normally outside the while loop.
    4. Fixed a bug that printing current queue in process log can be inaccurate since
    multiple threads modifying the queue in between printing.
    5. Optimized performance by moving unnecessary operations outside locks
    
    
    
    Review by Ribhi:
    1. Throughout your code, you used myQueue.size() without any protection. 
        This would cause unpredictable behavior (mostly a segfault or a deadlock) 
        if the queue is modified while .size() is executing
    2. After correcting issue #1 for you and testing your code, it still dead-locked 
        when running 4 generators and 1 adder.  All threads get stuck waiting on each other.
    
    Change log:
    1. Removed excessive process log
    2. Added protection when accessing myQueue.size() for all places.
        This resulted in lower performance, but ensures correctness
    3. Resolved deadlock by notifying both thread groups before any of the thread
        starts to wait. Since we have different mutexes, it has a chance that when 
        one generator thread notifies one adder thread but no adder thread is currently
        waiting. And vice versa. Hence we may reach a deadlock where all threads are waiting
        for notification but no one receives any. Notify other threads right before 
        one thread starts to wait can resolve this problem.
    4. The above changes work fine for any configuration except for 1 generator thread
    	and 1 adder thread. Back to Single mutex resolves this problem and the performance
    	was actually not influenced by using single mutex
    */


class Solution {
public:
	Solution(int n) : N(n)
	{
		for (int i = 0; i< 10; i++) occurence[i] = 0;
		numToCreate = N;
	}
	/*
    	check to see if the queue is not full
    	Not full: return true
	*/
	// Resolve Issue 1: accessing myQueue.size() without locking the queue 
	bool queue_available() {
		//no need to lock here since already locked outside
		return myQueue.size() < 10;
	}
	/*
    	check to see if the queue is not empty or there are no numbers to be created left
    	Not empty or numToCreate == 0: return true
	*/
	bool queue_nonempty() {
		//no need to lock here since already locked outside
		return myQueue.size() > 0 || numToCreate == 0;
	}
	bool whileCondition() {
		std::unique_lock<mutex> tLock(mtx_queue);
		return numToCreate > 0 || myQueue.size() > 0;
	}
	/*
	    Thread function for the first two threads
	*/
	void createRandomInt(int id)
	{
		while (numToCreate > 0)
		{
			unique_lock<mutex> lock(mtx_queue);
			while (!queue_available())
			{
				if (PROCESS_LOG)
				{
					mtx_cout.lock();
					cout << "Thread " << id << ": Waiting.." << endl;
					mtx_cout.unlock();
				}
				cv1.wait(lock);
			}

			/*
    			Between the time this thread starts waiting for notification and
    			actually being notified by one of the increment thread, the other
    			integer creating thread could have created some integers already.
    			Hence we need to check if numToCreate is 0 or not. If there are
    			no integers to be created, we notify all other threads if
    			they are waiting, then exit this function.
			*/
			if (numToCreate == 0)
			{
				if (PROCESS_LOG)
				{
					mtx_cout.lock();
					cout << "Thread " << id << ": All done. Notifying all other threads and exit" << endl;
					mtx_cout.unlock();
				}
				lock.unlock();
				cv2.notify_all();
				cv1.notify_all();
				return;
			}

			// generates random integer from 0-9
			static atomic<int> tCount(0);
			int randInt = tCount++ % 10;

			// inserting new integer to queue
			myQueue.push_back(randInt);
			numToCreate--;
			/*
    			BUG Fixed:
    			Current queue printing will sometimes be inaccurate since thread 3&4
    			might be popping during this time. Moving the printing inside the
    			mtx_queue lock can fix this bug.
			*/
			if (PROCESS_LOG)
			{
				mtx_cout.lock();
				cout << "Thread " << id << ": Inserted: " << randInt << endl;
				cout << "Thread " << id << ": # left to be created: " << numToCreate << endl;
				cout << "Thread " << id << ": Current queue: " << endl;
				for (int j = 0; j < myQueue.size(); j++)
				{
					cout << myQueue[j] << " ";
				}
				cout << endl;
				cout << endl;
				mtx_cout.unlock();
			}
			lock.unlock();
			cv2.notify_one();
		}
		
		// Here it means that the current thread just finished creating the last integer.
		if (PROCESS_LOG)
		{
			mtx_cout.lock();
			cout << "Thread " << id << ": All done. Notifying all other threads and exit" << endl;
			mtx_cout.unlock();
		}
		cv2.notify_all();
		cv1.notify_all();
		return;
	}
	/*
	Thread function for the second two threads
	*/
	void incrementOccurence(int id)
	{
		/*
		From the start, the queue size will be 0, but to make sure it goes
		we can make it loop until both numToCreate == 0 and myQueue.size() == 0
		This will be the moment when incrementing threads won't have any
		jobs left and gracefully exit
		*/
		while (whileCondition())
		{

			if (PROCESS_LOG)
			{
				mtx_cout.lock();
				cout << "Thread " << id << ": Trying to increment integer on queue." << endl;
				mtx_cout.unlock();
			}
			
			/*
			we use the second condition variable to make this thread wait until
			some integer creating thread does his job and makes the queue not
			empty again
			*/
			unique_lock<mutex> lock(mtx_queue);
			while (!queue_nonempty())
			{
				if (PROCESS_LOG)
				{
					mtx_cout.lock();
					cout << "Thread " << id << ": Waiting for Thread 1&2 to fill the queue." << endl;
					mtx_cout.unlock();
				}
				cv2.wait(lock);
			}

			/*
			Now we can have this thread notified because some integer creating
			thread just added an integer and need it to be incremented.
			Or we can have all integers already created and the queue is also
			empty, which means this thread can exit, after notifying all other
			threads which are still waiting.
			*/
			if (numToCreate == 0 && myQueue.size() == 0)
			{
				if (PROCESS_LOG)
				{
					mtx_cout.lock();
					cout << "Thread " << id << ": All done. Notifying all other threads and exit" << endl;
					mtx_cout.unlock();
				}
				lock.unlock();
				cv1.notify_all();
				cv2.notify_all();
				return;
			}


			int front = myQueue.front();
			myQueue.pop_front();

			// update occurence array
			occurence[front] ++;

			if (PROCESS_LOG)
			{
				mtx_cout.lock();
				cout << "Thread " << id << ": Queue popped: " << front << endl;
				cout << "Thread " << id << ": Current queue: " << endl;
				for (int j = 0; j < myQueue.size(); j++)
				{
					cout << myQueue[j] << " ";
				}
				cout << endl;
				cout << endl;
				mtx_cout.unlock();
			}

			// if there are still integers to be created, just notify a waiting thread
			if (numToCreate > 0)
			{
				if (PROCESS_LOG)
				{
					mtx_cout.lock();
					cout << "Thread " << id << ": Notifying thread 1&2 to continue adding. " << endl;
					mtx_cout.unlock();
				}
				lock.unlock();
				cv1.notify_one();
			}
		}
		if (PROCESS_LOG)
		{
			mtx_cout.lock();
			cout << "Thread " << id << ": All done. Notifying all other threads and exit" << endl;
			mtx_cout.unlock();
		}
		cv2.notify_all();
		cv1.notify_all();
		return;
	}

	bool run();

private:
	const int		        N;
    atomic<int>             numToCreate;
	int                     totalNum;
	int                     occurence[10];
	vector<thread>          threads;
	mutex                   mtx_queue;     //mutex for queue modification
	mutex                   mtx_cout;      //mutex for cout
	deque<int>              myQueue;
	condition_variable      cv1;
	condition_variable      cv2;
};

bool Solution::run()
{
	bool tPass = true;
	int tThreadID = 1;
	for (int i = 1; i <= 4; ++i)
		threads.emplace_back(&Solution::createRandomInt, this, tThreadID++);

	for (int i = 1; i <= 1; ++i)
		threads.emplace_back(&Solution::incrementOccurence, this, tThreadID++);


	for (auto& th : threads) th.join();
	cout << endl;
	/*
	cout << "The Randomly generated Integer array is: " << endl;
	for (int i = 0; i<randomInts.size() - 1; i++)    cout << randomInts[i] << ", ";
	cout << randomInts[randomInts.size() - 1] << endl;
	cout << endl;
	*/
	cout << "The Occurence array is: " << endl;
	int i;
	for (i = 0; i<9; i++)
	{
		cout << occurence[i] << ", ";
		if (occurence[i] != N / 10)
		{
			tPass = false;
		}
	}
	cout << occurence[9] << endl;
	return tPass;
}

int main()
{
	/*
	cout << "Please enter a positive integer N: ";
	string str;
	string::size_type sz;
	cin >> str;
	while (stoi(str, &sz) <= 0)
	{
		cout << "Please enter a positive integer N: ";
		cin >> str;
	}
	int N = stoi(str, &sz);
	cout << "Enable Process Log? (Y/N) ";
	cin >> str;
	if (str == "N" || str == "n")     PROCESS_LOG = 0;

	Solution mySol(N);

	clock_t t = clock();
	mySol.run();


	cout << endl;
	t = clock() - t;
	printf(" Runtime is %2f seconds.\n", ((float)t) / CLOCKS_PER_SEC);
	cout << "Press any key to exit. ";
	_getch();
	*/
	int i;
	for (i = 0; i<200; ++i)
	{
		Solution mySol(1000000);

		clock_t t = clock();
		if (!mySol.run()) break;


		cout << endl;
		t = clock() - t;
		printf("Run %d: Runtime is %2f seconds.\n", i, ((float)t) / CLOCKS_PER_SEC);
	}
	return 0;
}
