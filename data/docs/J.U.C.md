# 第一章 Atomic

## AtomicInteger

`addAndGet`、`incrementAndGet`这俩方法底层就是通过一套死循环循环调用`compareAndSetInt`完成线程安全的“加法”操作。当然，开发人员也可以自己死循环循环调用`compareAndSet`方法完成类似操作。

## AtomicReference

像AtomicInteger，都是对原子数据进行原子操作。那么如果想对多个共享变量同时更新呢？可以将这些共享变量封装到一个类里，再通过类实例进行比较和替换，实现“并发修改多个共享变量”。

# 第二章 AQS

> 全称：AbstractQueuedSynchronizer，是J.U.C中各种锁实现的基石。

## 原理

- AQS有`int state`和**CLH队列**两个关键属性
- 如果被请求的共享资源没有被占用，那么就把请求资源的线程设置为有效的线程，运行申请，并且把共享资源设置为锁定状态，即`state + 1`
- 如果被请求的共享资源已经被其他线程占用，那么当前线程就会被加入到一个等待队列中，即**CLH队列**

## state

- 当有线程获取到共享资源，state就会加1，该线程可以重复获取线程，那么state就累加。

- 每释放一次就会减1，直到全部释放，就会变成0。此时就可以从CLH队列中获取下一个Node中的线程来获取共享资源。

## CLH (Craig, Landin, and Hagersten)

CLH队列是一个虚拟的双向队列。

它把每一个请求共享资源的线程封装成一个CLH节点-Node。每一个Node拥有以下属性

- 线程的引用 `(Thread thread)`
- 当前Node的前驱Node `(Node prev)`
- 当前Node的后继Node `(Node next)`
- 当前节点在队列当中的状态 `(int waitStatus)`

# 第三章 ReentrantLock

> ReentrantLock是J.U.C包提供一种互斥锁，基于AQS实现。作用类似于synchronized，但使用方法有一些区别。

## 构造函数

``` java
// 公平锁
ReetrantLock lock1 = new ReetrantLock(true);

// 非公平锁、
ReetrantLock lock2 = new ReetrantLock(false);
ReetrantLock lock3 = new ReetrantLock();
```

## `lock()` 加锁

当多个线程同时尝试调用lock.lock()方法，只有其中一个线程可以获取锁，其余线程都要主动等待。

## `unlock()` 解锁

一般放在finally方法里，表示获取锁的线程释放锁。

## tryLock() 加锁

```java
// 无参
lock.tryLock();

// 有参
lock.tryLock(long timeout, TimeUnit unit);
```

- 无参：当调用`lock.tryLock()`时
  - 如果lock还未被占用，则立即获取锁，并返回true
  - 如果lock已被占用，则当前线程不会阻塞等待，而是直接返回false，直接继续往下执行
- 有参：当调用`lock.tryLock()`时
  - 如果当前线程在timeout时间内成功获取锁，则返回true
  - 如果timeout时间到了，当前线程仍未获取锁，则不再等待，直接返回false，继续往下执行
  - 如果当前线程在timeout时间内被中断，则当前线程会抛出**InterruptException**，也会终止等待

## lockInterruptibly() 加锁

如果一个线程调用`lock.tryLock()`时，锁已经被其他线程持有了，那么这个线程同样会进入阻塞状态，这点同`lock()`方法。

但是，如果锁一直没被释放呢？阻塞的线程会越来越多，这些线程都在进行长时间无意义的等待。

因此，就有了`lockInterruptibly()`方法，和`lock()`方法不同的是，只要当前线程收到了中断请求（即有其他线程调用了当前线程的`interrupt()`方法），那么它就会立即响应中断，终止等待，并抛出**InterruptException**异常。

## ReentrantLock VS synchronized

### 使用方法上的区别

- ReentrantLock可以提供公平+非公平两种特性，而synchronized是非公平的
- ReentrantLock的加锁和解锁操作都需要手动进行，一定不能忘记释放锁。而synchronized是自动加锁解锁的
- ReentrantLock提供了`lock.tryLock()`这样的尝试性获取锁的特性
- ReentrantLock提供了`lock.lockInterruptibly()`这样的，可以让在获取不到锁，在阻塞等待的线程被提前"唤醒"的中断式加锁

### 锁的实现方式不一样

- synchronized加锁过程，设计了JVM底层的锁升级过程，还可能涉及锁粗化、锁消除
- ReentrantLock是基于AQS来实现的

