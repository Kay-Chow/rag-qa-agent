# Java 并发编程系统笔记

---

# 第一章 并发编程概述

## 什么是并发与并行

在学习 Java 并发编程之前，首先需要区分两个容易混淆的概念：并发和并行。

**并发**通常是指在同一时间段内处理多个任务。对于单核 CPU 而言，同一时刻只能执行一个任务，但操作系统可以通过时间片轮转、线程调度和中断机制，在多个任务之间快速切换，使用户感觉多个任务在“同时”执行。

**并行**则是指在同一时刻真正有多个任务同时执行。并行通常依赖多核 CPU 或多个处理器，不同任务可以被分配到不同核心上同时运行。

简言之，并发强调“交替执行”，并行强调“同时执行”。并发是程序设计层面的组织方式，并行则更依赖硬件计算资源。

## 什么是上下文切换

CPU 在执行线程时，并不会一直运行某一个线程。当线程的时间片用完，或者线程因为 I/O 操作进入阻塞状态时，操作系统会暂停当前线程，并切换到另一个可运行线程。

在切换过程中，系统需要保存当前线程的运行状态，例如程序计数器、寄存器状态、栈信息等，并加载下一个线程的运行状态。这个过程被称为**上下文切换**。

上下文切换是并发运行的基础，但它本身也会带来性能开销。线程数量过多或调度过于频繁时，CPU 会将较多时间消耗在线程切换上，而不是用于真正执行业务逻辑。

## 单核处理器为什么也需要并发

有必要，程序执行并不总是 CPU 密集型计算。很多任务都包含 I/O 操作，例如网络请求、磁盘读写、数据库访问等。当一个任务等待 I/O 响应时，如果程序采用串行方式，其他任务只能被迫等待；而如果采用并发方式，CPU 可以切换到其他任务继续执行。

这就是并发的重要价值---**隐藏延迟**，可以提高资源利用率和系统吞吐量。

## 并发编程的主要挑战

并发编程虽然能够提高系统吞吐量和资源利用率，但也会引入一系列复杂问题。

### 上下文切换开销

线程并不是越多越好。线程数量过多会导致上下文切换频繁，反而降低程序性能。因此，在并发程序设计中，需要合理控制线程数量，减少不必要的线程切换。

### 线程安全问题

多个线程同时访问共享变量时，如果没有适当的同步机制，可能会导致数据不一致。例如，多个线程同时对同一个变量执行自增操作，最终结果可能小于预期值。

线程安全问题本质上来自共享资源的并发访问。解决这一问题通常需要借助锁、CAS、volatile、线程隔离等机制。

### 死锁问题

死锁是指多个线程相互等待对方持有的资源，导致所有线程都无法继续执行。例如，线程 A 持有锁 1 并等待锁 2，线程 B 持有锁 2 并等待锁 1，二者就会陷入死锁。

避免死锁通常需要破坏死锁产生的条件，例如固定加锁顺序、设置超时时间、减少嵌套锁等。

### 资源限制问题

并发程序的性能不仅受 CPU 限制，还受内存、磁盘 I/O、网络带宽、数据库连接数等资源限制。如果资源瓶颈没有解决，单纯增加线程数并不能提升性能，反而可能导致系统过载。

---

# 第二章 Java 线程基础

## 什么是进程与线程

现代操作系统在运行一个程序时，会为其创建一个进程。例如，启动一个 Java 程序时，操作系统会创建一个 Java 进程。

进程是资源分配的基本单位，每个进程拥有相对独立的内存空间。线程则是操作系统调度的基本单位，也被称为轻量级进程。在一个进程内部，可以创建多个线程，这些线程共享进程的堆内存和方法区资源，但每个线程又拥有自己的程序计数器、虚拟机栈和本地方法栈。

## Java 线程的创建方式

Java 中常见的线程创建方式主要有三种。

第一，继承 `Thread` 类，并重写其 `run()` 方法。

```java
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("Thread is running");
    }
}
```

第二，实现 `Runnable` 接口，并将任务对象传入 `Thread`。

```java
class MyRunnable implements Runnable {
    @Override
    public void run() {
        System.out.println("Runnable is running");
    }
}
```

第三，实现 `Callable` 接口，并通过 `Future` 获取线程执行结果。

```java
class MyCallable implements Callable<Integer> {
    @Override
    public Integer call() {
        return 1;
    }
}
```

其中，`Runnable` 没有返回值，`Callable` 可以返回执行结果并抛出异常。因此，如果任务需要返回值，通常使用 `Callable` 与 `Future` 配合。

## Java 线程状态

Java 线程的状态由 `Thread.State` 定义，主要包括以下六种。

### NEW

`NEW` 表示线程已经被创建，但尚未调用 `start()` 方法。此时线程对象已经存在，但还没有真正交给操作系统调度。

### RUNNABLE

`RUNNABLE` 表示线程处于可运行状态。Java 将操作系统中的 Ready 和 Running 两种状态统一归为 RUNNABLE。也就是说，线程可能正在运行，也可能正在等待 CPU 调度。

### BLOCKED

`BLOCKED` 表示线程因为竞争排他锁失败而进入阻塞状态。

需要注意的是，Java 中的 BLOCKED 与操作系统中的阻塞状态并不完全相同。操作系统层面的阻塞可能来自 I/O 等待，而 Java 中的 BLOCKED 主要指等待进入 monitor 锁。

### WAITING

`WAITING` 表示线程进入无限期等待状态，需要等待其他线程显式唤醒。常见方法包括：

- `Object.wait()`
- `Thread.join()`
- `LockSupport.park()`

### TIMED_WAITING

`TIMED_WAITING` 表示线程进入有时间限制的等待状态，等待时间结束后可以自动返回。常见方法包括：

- `Thread.sleep(long millis)`
- `Object.wait(long timeout)`
- `Thread.join(long millis)`
- `LockSupport.parkNanos(long nanos)`
- `LockSupport.parkUntil(long deadline)`

### TERMINATED

`TERMINATED` 表示线程执行完毕，生命周期已经结束。

## 守护线程

守护线程是一类支持型线程，主要用于后台调度和辅助性工作。垃圾回收线程就是典型的守护线程。

## 线程间通信方式

Java 中常见的线程间通信方式包括：

- `volatile`
- `synchronized`
- `wait / notify / notifyAll`
- `Thread.join()`
- `ThreadLocal`
- `LockSupport`
- 并发工具类，例如 `CountDownLatch`、`Semaphore` 等

---

# 第三章 Java 内存模型

## 为什么需要 Java 内存模型

不同硬件平台和操作系统在内存访问、缓存一致性和指令重排序等方面存在差异。如果 Java 程序直接依赖底层硬件行为，就很难保证跨平台运行结果的一致性。

Java 内存模型，其主要作用就是屏蔽不同硬件和操作系统之间的内存访问差异。它主要关注的是：在多线程环境下，变量如何从主内存读取到线程工作内存，以及线程对变量的修改如何同步回主内存。

## 主内存与工作内存

在 Java 内存模型中，所有共享变量都存储在主内存中。每个线程都有自己的工作内存，线程对变量的读取和修改通常发生在自己的工作内存中。

线程不能直接访问其他线程的工作内存。如果线程之间需要传递变量值，就必须通过主内存完成。

## 并发编程三要素

Java 内存模型主要围绕三个核心问题展开：原子性、可见性和有序性。

### 原子性

原子性是指一个操作不可被中断，要么全部执行成功，要么完全不执行。

例如，对基本类型变量的简单读写通常具有原子性，但 `i++` 并不是原子操作。因为 `i++` 实际上包含读取、加一、写回三个步骤，多线程同时执行时可能出现数据竞争。

操作系统通过总线锁和缓存错来保证原子性。

Java 中通常通过 `synchronized`、`Lock` 或 CAS 来保证复合操作的原子性。

#### CAS是什么

CAS 是 Compare And Swap 的缩写，中文通常称为“比较并交换”。它是一种无锁算法，常用于实现乐观锁。

CAS 涉及三个操作数：

- V：需要读写的内存值；
- A：预期值；
- B：准备写入的新值。

CAS 的基本逻辑是：只有当内存值 V 等于预期值 A 时，才将 V 更新为 B；否则不进行更新。

#### CAS的典型问题

##### ABA 问题

ABA 问题是 CAS 的经典问题。

假设一个变量最初为 A，线程 1 读取到 A。随后线程 2 将变量从 A 改为 B，又从 B 改回 A。线程 1 再次执行 CAS 时，发现变量仍然是 A，于是认为变量没有变化，但实际上它已经被修改过。

解决 ABA 问题的常见方法是引入版本号。例如，将变化过程从：

```text
A -> B -> A
```

变为：

```text
1A -> 2B -> 3A
```

Java 中的 `AtomicStampedReference` 就可以通过版本戳解决 ABA 问题。

##### 自旋时间过长

CAS 失败后通常会不断重试。如果竞争非常激烈，线程可能长时间自旋，占用大量 CPU 资源。

因此，在高竞争场景下，CAS 未必比锁更高效，有时需要结合锁、限流或退避策略。

##### 只能保证单个变量的原子性

CAS 通常只能保证单个共享变量的原子更新。如果需要同时更新多个变量，单纯使用 CAS 就会比较困难。

解决思路包括：

- 将多个变量封装到一个对象中，使用 `AtomicReference` 更新整个对象；
- 使用锁保护多个变量的复合更新；
- 使用支持版本控制的数据结构。

### 可见性

可见性是指一个线程对共享变量的修改，能够被其他线程及时看到。

如果线程 A 修改了变量，但该修改一直停留在线程 A 的工作内存中，没有同步回主内存，那么线程 B 就可能读取到旧值。

Java 中可以通过 `volatile`、`synchronized`、`final` 等机制保证可见性。

### 有序性

有序性是指程序执行的顺序符合预期。

为了提高执行效率，编译器和处理器可能会对指令进行重排序。在单线程环境下，重排序不会改变程序最终结果；但在多线程环境下，重排序可能导致难以预期的问题。

Java 内存模型通过 happens-before 规则对多线程之间的执行顺序进行约束。

## happens-before 原则

happens-before 是 Java 内存模型中判断操作之间可见性和有序性的核心规则。如果操作 A happens-before 操作 B，那么 A 的执行结果对 B 可见，并且 A 的执行顺序先于 B。

常见 happens-before 规则包括：

1. 程序顺序规则：同一个线程内，前面的操作 happens-before 后面的操作。
2. 监视器锁规则：对一个锁的解锁 happens-before 后续对这个锁的加锁。
3. volatile 变量规则：对一个 volatile 变量的写 happens-before 后续对这个 volatile 变量的读。
4. 线程启动规则：调用线程的 `start()` 方法 happens-before 被启动线程中的任意操作。
5. 线程终止规则：线程中的所有操作 happens-before 其他线程检测到该线程终止。
6. 线程中断规则：对线程调用 `interrupt()` happens-before 被中断线程检测到中断事件。
7. 传递性规则：如果 A happens-before B，B happens-before C，那么 A happens-before C。

## volatile 的内存语义

`volatile` 是 Java 中用于保证变量可见性和一定有序性的关键字。

当一个变量被 `volatile` 修饰后，一个线程对该变量的写操作会立即刷新到主内存；其他线程读取该变量时，会从主内存重新加载最新值。因此，`volatile` 可以保证变量修改对其他线程可见。

此外，`volatile` 还可以禁止特定类型的指令重排序。对 volatile 变量的写操作，happens-before 后续对该变量的读操作。

但是，`volatile` 不能保证复合操作的原子性。例如：

```java
volatile int count = 0;
count++;
```

即使 `count` 被 volatile 修饰，`count++` 仍然不是线程安全的，因为它包含多个步骤。

## synchronized 的内存语义

`synchronized` 不仅可以保证同一时间只有一个线程进入同步代码块，还可以保证内存可见性。

根据 Java 内存模型的规定，线程在释放锁之前，必须将工作内存中对共享变量的修改刷新到主内存；线程在获取锁之后，会重新从主内存读取共享变量的值。

因此，`synchronized` 同时具备原子性和可见性。

## final 的内存语义

`final` 也可以提供一定的可见性保证。被 `final` 修饰的字段在构造方法中完成初始化后，只要构造过程中没有发生 `this` 引用逃逸，其他线程就能够正确看到 final 字段的值。

因此，在不可变对象设计中，`final` 是一个非常重要的关键字。

---

# 第四章 Java 锁机制

## synchronized 的基本使用

### 修饰普通方法

当 `synchronized` 修饰普通实例方法时，锁对象是当前实例对象，即 `this`。

```java
public synchronized void method() {
    // 同步代码
}
```

### 修饰静态方法

当 `synchronized` 修饰静态方法时，锁对象是当前类对应的 `Class` 对象。

```java
public static synchronized void method() {
    // 同步代码
}
```

### 修饰代码块

当 `synchronized` 修饰代码块时，锁对象由括号中的对象决定。

```java
synchronized (this) {
    // 同步代码
}
```

这种方式更加灵活，可以缩小锁的范围，降低锁竞争。

## synchronized 的底层基础：对象头与 Mark Word

Java 对象在内存中包含对象头、实例数据和对齐填充。其中，对象头中的 Mark Word 与锁状态密切相关。

Mark Word 会根据对象所处的锁状态存储不同信息，例如：

- 对象 hashCode
- GC 分代年龄
- 偏向锁线程 ID
- Lock Record 指针
- Monitor 指针
- 锁标志位

## Monitor 监视器

在重量级锁状态下，`synchronized` 依赖 Monitor 监视器实现。

同步代码块在字节码层面通常会对应 `monitorenter` 和 `monitorexit` 指令，分别表示进入和退出同步区域。

Monitor 主要包含以下结构：

- `Owner`：当前持有锁的线程。
- `EntryList`：竞争锁失败后等待获取锁的线程集合。
- `WaitSet`：调用 `wait()` 后释放锁并进入等待状态的线程集合。
- `count`：用于记录锁重入次数。

当线程进入同步代码块时，需要尝试获取 Monitor；当线程退出同步代码块时，需要释放 Monitor。如果多个线程同时竞争同一个 Monitor，就会产生阻塞和唤醒过程。

## 锁的优化

在 JDK 1.6 之前，`synchronized` 通常被认为是重量级锁，性能开销较大。JDK 1.6 之后，JVM 对锁进行了大量优化，包括偏向锁、轻量级锁、自旋锁、锁消除、锁粗化等机制。

### 自旋锁

当一个线程第一次获取锁失败时，JVM 不一定立即将其挂起，而是让它在一段时间内循环尝试获取锁，这个过程称为自旋。

自旋的好处是避免线程挂起和恢复带来的上下文切换开销。如果锁很快被释放，自旋线程就可以直接获得锁。

但自旋也会消耗 CPU 资源。如果锁长时间无法释放，自旋会造成浪费。因此，自旋通常需要设置上限。

### 锁消除

锁消除是指 JVM 即时编译器在运行时发现某段同步代码不可能存在共享数据竞争，就会自动消除这部分加锁操作。

### 锁粗化

通常情况下，锁的粒度越小，程序并发性越好。但如果一段代码中对同一个对象反复加锁和解锁，例如在循环体内频繁执行同步操作，就会产生不必要的性能开销。

此时 JVM 可能会将多个连续的加锁、解锁操作合并为一次更大范围的加锁，即锁粗化。

### 锁升级过程

1. 一个被synchronized修饰的同步代码块，没被用过。这时候，线程A过来尝试执行它，会先去看他对象头里的**Mark Word**文件，会发现它锁标志位为01，且没有保存线程Id，或者对象的**hashCode**，那么它就是**匿名偏向锁**。线程A可以直接获取该锁，并把自己的线程Id写进**Mark Word**中。这个时候，就从**无锁**，或者更准确一点，就叫**匿名偏向锁**，升级到了**偏向锁**。
2. 这个时候，又有一个线程B来尝试执行该同步代码块，也先去查看对象头，发现**Mark Word**里已经保存了一个线程Id，而且不是自己，已经名花有主了。这个时候会触发**STW（Stop The Word）**，由线程B去看里面线程Id对应的线程，也就是线程A的状态：
   1. 如果A已经执行完了，那好说，直接就是一个**偏向锁撤销**，撤销回不可偏向锁的状态，然后线程B再来获取锁，而不可偏向锁在有线程进来的时候，都会直接升级到**轻量级锁**，所以B最后会获得一个轻量级锁，并把**Mark Word**放入**Lock Record**中，对象头里保存该**Lock Record**对应的地址，以及锁标识位改成00
   2. 如果A仍在执行中，B会自旋获取锁，获取到了还好，就是跟刚刚一样，升级到轻量级锁；若自旋完还没获取到，或者说自旋过程中，还有第三者线程C来参与竞争，那么也会进行一个偏向锁撤销操作，然后直接升级到**重量级锁**，创建一个**Monitor对象**，并在对象头里保存该**Monitor对象**的地址，以及锁标志位改成10

### 无锁与匿名偏向锁

当对象尚未被线程使用时，它可能处于无锁状态，普通无锁状态的标志位为0 01，其中0为偏向位。如果启用了偏向锁机制，对象也可能处于匿名偏向状态，标志位为1 01，同时其对象头中偏向线程Id为空。

JDK 8中，默认开启延迟偏向，JVM启动4s后，自动开启偏向。延迟4s的原因是JVM刚启动时有大量初始化操作，存在激烈的锁竞争，偏向锁竞争时撤销开销极大，反而会拖慢启动速度。

### 偏向锁

偏向锁的目标是优化“无竞争但同一线程重复加锁”的场景。

如果一个对象已经偏向线程 A，那么线程 A 后续再次进入该同步代码块时，通常不需要执行 CAS 操作，只需要检查 Mark Word 中记录的线程 ID 是否为自己即可。

### 偏向锁撤销

有四种场景会进行偏向锁的撤销：

- 线程B来竞争线程A的偏向锁，会先**STW**，然后检查A是否还在同步块内，不在的话就会撤销偏向，然后升级到轻量级锁
  - 为啥不直接CAS替换成线程B的线程Id呢？因为偏向锁为了极致的无竞争性能，他不想一个个做CAS的操作。除非是批量重偏向
  - 为啥不直接升级成轻量级锁呢？偏向锁的**Mark Word**存放的是线程Id，轻量级锁存的是**Lock Record**地址，不能无缝切换

- biased状态，原来放hash的地方现在已经放了线程ID，这时候如果再计算hashCode，就会直接撤销偏向锁，变成无锁或者轻量级锁，无锁的时候对象头里**Mark Word**可以保存hashCode，轻量级锁对象头会指向**Lock Record**，里面会保存带hashCode的**Mark Word**
  - 所以又引出来一个点，如果对象调用了原生的Object.hashCode()，会强制写入**Mark Word**，这个时候对象就会永久禁用偏向锁，偏向位强制清0，因为没地方放线程Id咯
- 调用wait/notify/notifyAll时，该机制会直接撤销偏向状态，升级为重量级锁，锁标志位为10
- 最后就是**批量重偏向**或者**批量撤销**的场景

### 批量重偏向与批量撤销

如果某一类对象频繁从一个线程偏向另一个线程，JVM 可能认为这些对象仍适合偏向锁，只是偏向对象需要调整。此时 JVM 可能执行批量重偏向，将一批对象的偏向线程改为新的线程。

如果竞争更加激烈，说明这一类对象已经不适合偏向锁，JVM 可能执行批量撤销，并禁止该类对象继续使用偏向锁。

### 轻量级锁

##### 加锁过程

- 首先在线程栈帧中创建一个**Lock Record**空间，拷贝当前**Mark Word**到该空间中
- 通过CAS操作，将**Mark Word**更新为指向**Lock Record**的指针
  - CAS成功，表示当前线程持有该对象的轻量级锁，将对象**Mark Word**中锁标志位改为00
  - CAS失败，则说明Mark Word已被其他线程修改过了，因为比较对象为拷贝后的**Mark Word**和当前**Mark Word**，既然被修改过了，就说明已经锁已经被其他线程占据了，那么就得去自旋获取锁了

##### 重入过程

- 看到轻量级锁标识位00时，看**Lock Record**指针地址，是否是自己在自己的栈内，是的话就是重入
- 在栈中新增一条**Lock Record**，这条不记录任何东西，单纯用来计数
- 解锁的时候，每退出一个synchronized，都会在栈中弹出一个**Lock Record**
- 直到弹出最后一个携带**Mark Word**信息的**Lock Record**时，才会用CAS来恢复对象头，锁标志为0 01，无锁

### 重量级锁

##### Monitor监视器

重量级的底层实现靠的是**Monitor监视器**。同步代码块在被反编译后，会输出monitorenter和monitorexit两种指令，分别代表获取锁和释放锁。

**Monitor监视器**对象是由底层C++代码实现的，主要包含以下几个部分：

- `header`：**Mark Word**初始值

- `EntryList`：竞争锁失败，进入阻塞等待的线程集合，**JVM会从里面随机选取线程获得锁，还可能被插队，是非公平的**
- `WaitSet`：获得过锁，但又释放了的线程集合。当`WaitSet`中的线程被`notify`/`notifyAll`唤醒时，又会进入`EntryList`队列等待获取锁。
- `owner`：当前获得锁的线程对象
- `count`：作为一个可重入锁，由`count`来计数，`owner`线程可以多次重复获得锁，每`monitorenter`一次，`count`都会+1，`monitorexit`一次，`count-1`，直到`count=0`时，当前线程就可以去`WaitSet`了

##### 轻量级锁升级为重量级锁过程

- 自旋失败，或者第三者线程参与竞争，JVM判断轻量竞争已经失效，需要阻塞队列，升级！！！
- 当前锁的持有者线程继续运行，不受影响，Lock Record也继续被它持有
- 在内存堆内开辟**Monitor监视器**，把**Monitor监视器**的owner标记为当前线程
- 操作**Mark Word**，清空原来的**Lock Record**地址，直接写入**Monitor监视器**地址，并永远指向该地址，然后把锁标志位改成10，重量级锁
- 其他所有抢锁失败的线程都丢到EntryList里，不再自旋，不再消耗CPU
- 升级到重量级锁之后，就永远不会退化了

##### 重量级锁的进入和释放过程

- 进入的时候也会在栈帧中新建**Lock Record**，但不保存信息
- 释放的时候跟轻量级锁一样，也需要一个个弹出**Lock Record**
- 线程主动释放**Monitor监视器**，设置其owner为null
- 从EntryList里面随机唤醒一个等待线程来抢占**Monitor监视器**

---

# 第五章 ThreadLocal

## 什么是 ThreadLocal

`ThreadLocal` 是 Java 提供的一种线程隔离机制。它可以让每个线程拥有变量的独立副本，从而避免多个线程之间相互影响。

最常用的就是保存用户登录信息。

## ThreadLocal 的底层原理

`ThreadLocal` 的数据并不是存储在 `ThreadLocal` 对象本身，而是存储在当前线程对象内部。

在 `Thread` 类中，有一个字段：

```java
ThreadLocal.ThreadLocalMap threadLocals;
```

当当前线程调用 `ThreadLocal.set(value)` 时，实际上是将当前 `ThreadLocal` 对象作为 key，将 value 作为值，存入当前线程的 `threadLocals` 中。

当当前线程调用 `ThreadLocal.get()` 时，也是从当前线程自己的 `threadLocals` 中，根据当前 `ThreadLocal` 对象查找对应的 value。

因此，不同线程访问同一个 `ThreadLocal` 对象时，实际上访问的是各自线程对象内部的不同值。

## ThreadLocalMap

`ThreadLocalMap` 是 `ThreadLocal` 的内部静态类，可以理解为一种特殊的 HashMap。

它的底层结构是 Entry 数组。每个 Entry 中保存一组 key-value，其中 key 是 `ThreadLocal` 对象，value 是线程局部变量的值。

特殊之处在于，Entry 的 key 是弱引用：

```java
static class Entry extends WeakReference<ThreadLocal<?>> {
    Object value;
}
```

也就是说，当 `ThreadLocal` 对象没有被外部强引用时，垃圾回收可能会回收这个 key。但 Entry 中的 value 是强引用，不会因为 key 被回收而自动回收。

## ThreadLocal 的内存泄漏问题

如果 `ThreadLocal` 的 key 被垃圾回收，而 value 仍然保存在 `ThreadLocalMap` 中，就可能出现 key 为 null、value 仍然存在的 Entry。

在普通线程中，当线程结束后，线程对象会被回收，对应的 `ThreadLocalMap` 也会被回收，因此问题不一定明显。

但在线程池环境中，线程会被重复利用，核心线程可能长期存活。如果使用完 `ThreadLocal` 后不主动清理，value 可能长期保留在线程对象中，导致内存泄漏。

此外，线程复用还可能导致数据污染。例如，某个线程处理上一个请求时设置了用户信息，如果没有清理，下一个请求复用该线程时可能读取到旧的用户信息。

所以，用完后请在 finally 代码块中调用 `remove()` 方法。

---

# 第六章 Java 线程池

## ThreadPoolExecutor 核心参数

Java 线程池的核心类是 `ThreadPoolExecutor`，其构造方法如下：

```java
public ThreadPoolExecutor(int corePoolSize,
                          int maximumPoolSize,
                          long keepAliveTime,
                          TimeUnit unit,
                          BlockingQueue<Runnable> workQueue,
                          ThreadFactory threadFactory,
                          RejectedExecutionHandler handler)
```

各参数含义如下。

### corePoolSize

核心线程数。核心线程通常会长期存活，即使处于空闲状态也不会被回收，除非设置允许核心线程超时。

### maximumPoolSize

最大线程数。线程池中允许存在的最大线程数量。最大线程数与核心线程数之间的差值可以理解为临时线程或救急线程数量。

### keepAliveTime 与 unit

非核心线程的空闲存活时间。如果非核心线程空闲时间超过该值，就会被回收。

### workQueue

任务阻塞队列。当核心线程都在执行任务时，新提交的任务会进入阻塞队列等待执行。

### threadFactory

线程工厂，用于创建线程。通过自定义线程工厂，可以设置线程名称、是否为守护线程、异常处理器等。

### handler

拒绝策略。当线程池和阻塞队列都无法继续接收任务时，就会触发拒绝策略。

## 线程池的任务执行流程

线程池执行任务的大致流程如下：

1. 如果当前运行线程数小于核心线程数，直接创建核心线程执行任务；
2. 如果核心线程数已满，将任务放入阻塞队列；
3. 如果阻塞队列已满，且当前线程数小于最大线程数，创建非核心线程执行任务；
4. 如果当前线程数已经达到最大线程数，触发拒绝策略。

可以简化为：

```text
核心线程 -> 阻塞队列 -> 非核心线程 -> 拒绝策略
```

## 拒绝策略

Java 线程池内置了四种常见拒绝策略。

### AbortPolicy

默认拒绝策略。直接抛出 `RejectedExecutionException`，适用于关键业务场景，因为它可以明确暴露任务被拒绝的问题。

### DiscardPolicy

直接丢弃新提交的任务，不抛出异常。适用于对任务丢失不敏感的场景。

### DiscardOldestPolicy

丢弃队列中最旧的任务，然后尝试提交新任务。适用于允许丢弃旧任务、优先处理新任务的场景。

### CallerRunsPolicy

由提交任务的线程自己执行该任务。该策略可以减缓任务提交速度，形成一定的反压效果，适用于希望尽量不丢任务的场景。

## 如何确定核心线程数

线程池参数没有固定答案，需要结合任务类型、机器资源和业务目标综合确定。

### CPU 密集型任务

CPU 密集型任务主要消耗 CPU 计算资源，线程数不宜过多。常见经验值为：

```text
线程数 = CPU 核心数 + 1
```

多出的 1 个线程用于在某些线程因缺页中断等原因暂停时补充 CPU 利用率。

### I/O 密集型任务

I/O 密集型任务包含较多等待时间，例如网络请求、磁盘读写等。线程数可以适当设置得更大。常见经验值为：

```text
线程数 = CPU 核心数 × 2
```

但这只是经验值，实际还需要结合 I/O 等待时间、数据库连接池大小、下游服务承载能力等因素。

### 通用估算公式

较常见的估算公式为：

```text
线程数 = CPU 核心数 × 期望 CPU 利用率 × 总时间 / CPU 计算时间
```

其中：

```text
总时间 = CPU 计算时间 + 等待时间
```

等待时间越长，合理线程数通常可以越大。

## Executors 提供的线程池

`java.util.concurrent.Executors` 提供了一些快捷创建线程池的方法。

### FixedThreadPool

固定大小线程池。核心线程数等于最大线程数，使用无界阻塞队列。

适用于任务量相对稳定、任务执行时间较长的场景。

### CachedThreadPool

缓存线程池。核心线程数为 0，最大线程数非常大，使用 `SynchronousQueue`。

适用于任务数量较多但单个任务执行时间较短的场景。

### SingleThreadExecutor

单线程线程池。核心线程数和最大线程数都为 1，使用无界队列。

适用于需要保证任务按顺序执行的场景。

## 为什么不建议直接使用 Executors

很多开发规范不建议直接使用 `Executors` 创建线程池，主要原因在于其默认参数可能导致资源耗尽。

`FixedThreadPool` 和 `SingleThreadExecutor` 使用的阻塞队列默认容量非常大，可能堆积大量任务，最终导致 OOM。

`CachedThreadPool` 的最大线程数非常大，在高并发情况下可能创建大量线程，也可能导致 OOM。

因此，更推荐直接使用 `ThreadPoolExecutor`，明确指定核心线程数、最大线程数、队列容量、线程工厂和拒绝策略。

## 线程池状态

线程池主要包括以下状态。

### RUNNING

能够接收新任务，也能够处理阻塞队列中的任务。

### SHUTDOWN

不再接收新任务，但会继续处理阻塞队列中的已有任务。

### STOP

不接收新任务，也不处理阻塞队列中的任务，并会尝试中断正在执行的任务。

### TIDYING

所有任务都已终止，工作线程数为 0，线程池即将进入终止状态。

### TERMINATED

线程池已经完全终止。

## 阻塞队列汇总

线程池中的任务队列通常使用阻塞队列。常见阻塞队列如下。

### ArrayBlockingQueue

基于数组实现的有界阻塞队列，按照 FIFO 原则处理任务，支持公平锁和非公平锁。

### LinkedBlockingQueue

基于链表实现的阻塞队列。可以指定容量，如果不指定，默认容量为 `Integer.MAX_VALUE`，通常被视为无界队列。

### PriorityBlockingQueue

支持优先级排序的无界阻塞队列。元素需要实现比较规则，不能保证同优先级元素的顺序。

### DelayQueue

延迟队列，元素只有在延迟时间到期后才能被获取。其底层通常基于优先级队列实现。

### SynchronousQueue

不存储元素的阻塞队列。每一个 put 操作都必须等待一个 take 操作，反之亦然。`CachedThreadPool` 使用的就是这种队列。

### LinkedTransferQueue

基于链表实现的无界阻塞队列，实现了 `TransferQueue` 接口，可以在生产者和消费者之间直接传递元素。

### LinkedBlockingDeque

基于链表实现的双向阻塞队列，可以从队头和队尾插入或移除元素。

---

# 第七章 JUC 并发工具类

## JUC 概述

JUC 是 `java.util.concurrent` 的简称，是 Java 提供的并发工具包。相比直接使用 `synchronized` 和 `wait / notify`，JUC 提供了更丰富、更灵活的并发控制工具。

JUC 主要包括以下几类内容：

1. 显式锁，例如 `ReentrantLock`；
2. 同步器，例如 `CountDownLatch`、`CyclicBarrier`、`Semaphore`；
3. 并发容器，例如 `ConcurrentHashMap`；
4. 阻塞队列，例如 `ArrayBlockingQueue`、`LinkedBlockingQueue`；
5. 原子类，例如 `AtomicInteger`、`AtomicReference`；
6. 异步编程工具，例如 `CompletableFuture`。

## AQS

AQS 是 AbstractQueuedSynchronizer 的缩写，即抽象队列同步器。它是 JUC 中很多同步工具的底层基础。

AQS 的核心思想是：

- AQS有`int state`和**CLH队列**两个关键属性
- 如果被请求的共享资源没有被占用，那么就把请求资源的线程设置为有效的线程，运行申请，并且把共享资源设置为锁定状态，即`state + 1`
- 如果被请求的共享资源已经被其他线程占用，那么当前线程就会被加入到一个等待队列中，即**CLH队列**

### state

- 当有线程获取到共享资源，state就会加1，该线程可以重复获取线程，那么state就累加。

- 每释放一次就会减1，直到全部释放，就会变成0。此时就可以从CLH队列中获取下一个Node中的线程来获取共享资源。


### CLH (Craig, Landin, and Hagersten)

CLH队列是一个虚拟的双向队列。

它把每一个请求共享资源的线程封装成一个CLH节点-Node。每一个Node拥有以下属性

- 线程的引用 `(Thread thread)`
- 当前Node的前驱Node `(Node prev)`
- 当前Node的后继Node `(Node next)`
- 当前节点在队列当中的状态 `(int waitStatus)`

很多 JUC 工具都基于 AQS 实现，例如：

- `ReentrantLock`
- `Semaphore`
- `CountDownLatch`
- `ReentrantReadWriteLock`

AQS 将线程排队、阻塞和唤醒等复杂逻辑封装起来，使开发者可以在其基础上构建不同类型的同步器。

## ReentrantLock

`ReentrantLock` 是 JUC 中常用的可重入锁。它与 `synchronized` 一样，可以保证同一时刻只有一个线程访问临界区。

与 `synchronized` 相比，`ReentrantLock` 提供了更灵活的功能，例如：

- 可中断地获取锁；
- 可设置公平锁或非公平锁；
- 可尝试获取锁；
- 可绑定多个条件队列。

### 构造函数

```java
// 公平锁
ReetrantLock lock1 = new ReetrantLock(true);

// 非公平锁、
ReetrantLock lock2 = new ReetrantLock(false);
ReetrantLock lock3 = new ReetrantLock();
```

### `lock()` 加锁

当多个线程同时尝试调用lock.lock()方法，只有其中一个线程可以获取锁，其余线程都要主动等待。

```java
ReentrantLock lock = new ReentrantLock();

lock.lock();
try {
    // 临界区代码
} finally {
    lock.unlock();
}
```

使用 `ReentrantLock` 时，必须在 finally 中释放锁，否则可能导致死锁。

### `unlock()` 解锁

一般放在finally方法里，表示获取锁的线程释放锁。

###  `tryLock() `加锁

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

### `lockInterruptibly() `加锁

如果一个线程调用`lock.tryLock()`时，锁已经被其他线程持有了，那么这个线程同样会进入阻塞状态，这点同`lock()`方法。

但是，如果锁一直没被释放呢？阻塞的线程会越来越多，这些线程都在进行长时间无意义的等待。

因此，就有了`lockInterruptibly()`方法，和`lock()`方法不同的是，只要当前线程收到了中断请求（即有其他线程调用了当前线程的`interrupt()`方法），那么它就会立即响应中断，终止等待，并抛出**InterruptException**异常。

### ReentrantLock VS synchronized

#### 使用方法上的区别

- ReentrantLock可以提供公平+非公平两种特性，而synchronized是非公平的
- ReentrantLock的加锁和解锁操作都需要手动进行，一定不能忘记释放锁。而synchronized是自动加锁解锁的
- ReentrantLock提供了`lock.tryLock()`这样的尝试性获取锁的特性
- ReentrantLock提供了`lock.lockInterruptibly()`这样的，可以让在获取不到锁，在阻塞等待的线程被提前"唤醒"的中断式加锁

#### 锁的实现方式不一样

- synchronized加锁过程，设计了JVM底层的锁升级过程，还可能涉及锁粗化、锁消除
- ReentrantLock是基于AQS来实现的

## CountDownLatch

`CountDownLatch` 是一种倒计时同步工具。它允许一个或多个线程等待其他线程完成操作。

典型使用场景是：主线程等待多个子任务执行完成后再继续执行。

```java
CountDownLatch latch = new CountDownLatch(3);

for (int i = 0; i < 3; i++) {
    new Thread(() -> {
        try {
            // 执行任务
        } finally {
            latch.countDown();
        }
    }).start();
}

latch.await();
System.out.println("所有任务执行完成");
```

`CountDownLatch` 的计数器只能减少，不能重置。因此它适合一次性等待场景。

## CyclicBarrier

`CyclicBarrier` 是循环屏障。它允许一组线程互相等待，直到所有线程都到达某个屏障点后，再一起继续执行。

与 `CountDownLatch` 不同，`CyclicBarrier` 可以重复使用。

典型场景是多个线程分阶段执行任务，每一阶段都需要等待所有线程完成后再进入下一阶段。

```java
CyclicBarrier barrier = new CyclicBarrier(3, () -> {
    System.out.println("所有线程到达屏障点");
});
```

## Semaphore

`Semaphore` 是信号量，用于控制同时访问某个资源的线程数量。

例如，某个资源最多允许 5 个线程同时访问，就可以创建 5 个许可的信号量。

```java
Semaphore semaphore = new Semaphore(5);

semaphore.acquire();
try {
    // 访问受限资源
} finally {
    semaphore.release();
}
```

`Semaphore` 常用于限流、连接池控制和资源访问控制等场景。

## ConcurrentHashMap

`ConcurrentHashMap` 是线程安全的哈希表，适用于高并发读写场景。

相比早期的 `Hashtable`，`ConcurrentHashMap` 通过更细粒度的并发控制提高性能。JDK 8 之后，`ConcurrentHashMap` 主要采用 CAS 与 synchronized 结合的方式实现并发控制。

在高并发场景下，推荐使用 `ConcurrentHashMap` 替代普通的 `HashMap`，因为普通 `HashMap` 不是线程安全的。

## BlockingQueue

`BlockingQueue` 是阻塞队列接口，常用于生产者—消费者模型。

当队列为空时，消费者线程获取元素会被阻塞；当队列已满时，生产者线程插入元素会被阻塞。

常见实现包括：

- `ArrayBlockingQueue`
- `LinkedBlockingQueue`
- `PriorityBlockingQueue`
- `DelayQueue`
- `SynchronousQueue`

线程池中的任务队列通常就是通过阻塞队列实现的。

## Atomic 原子类

JUC 提供了多种原子类，用于在不显式加锁的情况下实现线程安全更新。

常见原子类包括：

- `AtomicInteger`
- `AtomicLong`
- `AtomicBoolean`
- `AtomicReference`
- `AtomicStampedReference`
- `LongAdder`

原子类底层通常基于 CAS 实现，适合对单个变量进行高效并发更新。

## CompletableFuture

`CompletableFuture` 是 Java 8 引入的异步编程工具。它可以用于异步任务编排，支持任务串行、并行、组合、异常处理等操作。

常见使用方式如下：

```java
CompletableFuture.supplyAsync(() -> {
    return "result";
}).thenApply(result -> {
    return result + " processed";
}).thenAccept(System.out::println);
```

`CompletableFuture` 的优势在于可以避免传统回调方式导致的代码嵌套，使异步任务编排更加清晰。

## JUC 工具类的选择建议

不同并发工具适用于不同问题：

| 问题类型 | 推荐工具 |
|---|---|
| 保护临界区 | synchronized / ReentrantLock |
| 高并发计数 | AtomicLong / LongAdder |
| 等待多个任务完成 | CountDownLatch |
| 多线程阶段性同步 | CyclicBarrier |
| 控制并发访问数量 | Semaphore |
| 生产者—消费者模型 | BlockingQueue |
| 高并发 Map | ConcurrentHashMap |
| 异步任务编排 | CompletableFuture |

选择并发工具时，应优先根据问题本身判断，而不是简单追求“更高级”的工具。并发编程的关键不是工具越多越好，而是用合适的工具解决合适的问题。

