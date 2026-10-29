# 第一章   Java程序设计概述

## JDK新特性

#### JDK 8

- lamda表达式
- HashMap重构

#### JDK 9

- String底层结构从char[]变成了byte[]

#### JDK 10

- var关键字，终于不用写两遍类名了！！！

#### JDK 12

- switch表达式大升级：多个case标签可以合并了，且可以直接使用箭头返回值

```java
// JDK 12
public String newMultiSwitch(int day) {
    return switch (day) {
        case 1, 2, 3, 4, 5 -> "workday";
        case 6, 7 -> "weekend";
        default -> "invalid";
    };
}

// JDK < 12
public String oldMultiSwitch(int day) {
    switch (day) {
        case 1:
        case 2:
        case 3:
        case 4:
        case 5:
            return "workday";
        case 6:
        case 7:
            return "weekend";
        default:
            return "invalid";
    }
}
```

#### JDK 13

- 支持文本块，终于可以像Python一样使用三个引号来引用一段文本了，不用\n了！！！

```java
// JDK 13
public String getNewPrettyPrintJson() {
    return """
           {
                "firstName": "Piotr",
                "lastName": "Mińkowski"
           }
           """;
}

// JDK < 13
public String getOldPrettyPrintJson() {
    return "{\n" +
           "     \"firstName\": \"Piotr\",\n" +
           "     \"lastName\": \"Mińkowski\"\n" +
           "}";
}
```



# 第二章   Java的基本程序设计结构

## 基本类型和包装类型

### 基本类型

> 不包括String

- boolean - 1位
- byte - 8位
- char - 16位
- short - 16位
- int - 32位
- float - 32位
- long - 64位
- double - 64位

### 包装类型

- int —> Integer
- short—> Short
- long—> Long
- byte—> Byte
- float—> Float
- double—> Double
- char —> Character
- boolean —> Boolean

### 为啥有了基本类型还需要包装类型呢？

因为Java是一门面向对象的语言，为了让基本类型具备对象的性质，就需要用到包装类型。

基本类型主要优点就是简单、方便，比起对象来说占用的空间也会更少，但它不具备对象的性质。

## 字符串

### String、StringBuilder、StringBuffer的区别

- String不可变，StringBuilder和StringBuffer可变
- String、StringBuffer线程安全，StringBuilder非线程安全

#### String不可变的原因

- 底层存储字符的char[]数组被final修饰，且不向外提供任意可修改数组内容的方法
- 类本身也被final修饰，阻止通过继承的方式覆盖或扩展方法来达成修改char[]的目的

#### String不可变的好处

- **字符串常量池**：字符串属于常用类型，如果每个字符串都要新建一个对象，就很容易造成空间浪费，故Java虚拟机提出了**字符串常量池**的概念，如果两个字符串内容相同，那么两个字符串就可以指向同一个字符串对象，而不需要创建两个内容相同的字符串对象。
- **多线程安全**：由于字符串不可变，故不需要对其采取任何同步措施，便可安全地被多线程所共享，节省大量同步操作
- **固定的Hash值**：由于字符串不可变，故其Hash值夜不会发生变化。其实String类内部直接维护了一个字段直接持有其Hash值，在需要计算Hash值的地方就不需要再计算了，直接用！！！Map直呼内行！！！String:"我来组成Key部！！！"

#### String + String是怎么做到的？

字符串使用加法运算时，实际上是创建了一个StringBuilder对象，然后执行append方法。

**因此，不要在循环体内直接使用String + String！！！**

会重复创建超级多StringBuilder对象，推荐在循环体开始之前就定义好一个StringBuilder对象，然后在循环体内对它进行操作。

#### String的字符常量池与new String

```java
String m = "hello";
String n = "hello"; 
String u = new String(m);
String v = new String("hello");
```

1. 分配一个长度为5的char数组，并在常量池分配一个由这个char数组组成的字符串，然后由m去引用该字符串。
2. 常量池中已有"hello"字符串，所以n直接引用该字符串----n和m引用同一个对象。
3. 在堆内存中新创建一个字符串对象，并将它指向常量池中已创建的对象。
4. 同3，也会在堆内存中创建一个字符串对象。

**所以String类型最好也别用 ==比较，谁知道他是不是 new String创建的呢？new出来的内存地址当然不一样！！！**

#### String类的offset和count属性

```java
String m = "hello,world";
String u = m.substring(2, 10);
String v = u.substring(4, 7);

u.getOffset == 2;
u.getCount == 8;

v.getOffset == 6;
v.getCount == 3;
```

可以看出，其实m、u、v都是指向字符串常量池中同一个对象，就是根据offset和count来区分引用哪些内容。

细，实在是太细了！！！



# 第三章   对象与类

## 面向过程 vs 面向对象

### 面向过程

优点：性能比面向对象高，因为类的调用需要实例化，开销会比较大，比较消耗资源。因此在单片机、嵌入式、Linux/Unix等场景中，一般采用面向过程开发，在类似场景中，性能是最重要的因素。

缺点：不如面向对象开发的程序易维护、易复用、易扩展。

### 面向对象

优点：易维护、易复用、易扩展。面向对象有着**封装、继承、多态三大特性**，可以设计出低耦合的系统，使系统更加灵活、更加易于维护。

缺点：性能不如面向过程。

## 封装

面向对象三大特性之一，为了安全访问对象，使用封装技术，将类的某些信息隐藏在类内部，不允许外部程序直接访问，而是通过该类提供的方法，如get和set，来实现对隐藏信息的操作和访问。

## static

### 静态字段

用的比较少，属于类，而不属于任何单个对象实例，所有实例都可对它进行操作。

### 静态常量

这个用的就非常多了，一般都用static final来定义。比如Math.PI。

### 静态方法

一般通过类名来直接调用静态方法，而不是通过对象实例来调用。

- 方法不需要访问对象状态，所有参数都通过显式参数来提供，比如Math.max()
- 方法只需要访问类的静态字段

### 工厂方法

```java
NumberFormat currencyFormatter = NumberFormat.getCurrencyInstance();
NumberFormat percentFormatter = NumberFormat.getPercentInstance();
double x = 0.1;
sout(currencyFormatter.format(x)); // $0.10
sout(percentFormatter.format(x)); // 10%
```

为啥不用构造器来new一个NumberFormat呢？

- 无法命名呀，构造器名字必须与类名相同，当想要多种方法构造不同的实例对象时，比如货币实例和百分百实例，就得用到工厂方法了
- 构造器得到的必是类名对应的类。而上述工厂方法返回的实际上是DecimalFormat类的对象，是NumberFomat的子类

### main方法

public static void main：哈哈哈哈哈，没想到吧，俺也是静态方法！

## final

### final修饰不可变字段

final修饰实例字段，则该字段必须在构造对象时初始化，且无法再修改该字段。比如修饰基本类型、String。**这种被final修饰的不可变字段被称为常量。**

### final修饰可变字段

```java
private final StirngBuilder sb;
```

这边会比较容易造成混乱，final关键字只是表示sb变量中的对象不会再指向另一个不同的StringBuilder对象，但是sb中对象的内容是可以更改的。

### final修饰类

不可被继承

### final修饰方法

不可被重写

##  序列化和反序列化

- 序列化是指将一个Java对象变成二进制内容，本质上就是一个`byte[]`数组
- 序列化后，可以把`byte[]`保存到文本中，或者把`byte[]`通过网络远程传输，这样，就相当于把Java对象存储到文件或者远程传输出去了
- 一个Java对象要能序列化，必须实现一个特殊的`java.io.Serializable`接口，它是一个**标记接口**，没有定义任何方法
- 有序列化，就有反序列化。反序列化就是把一个`byte[]`数组，变回Java对象，有了反序列化，保存在文件中的数据，以及网络上读取到的数据，变回Java对象了
- 反序列化时，由JVM直接构造出Java对象，**不调用构造方法**。**构造方法内部的代码，在反序列化时不会被执行**
- JDK序列化要通过`ObjectOutPutStream`，反序列化要通过`ObjectInputStream`。反序列话时常见的错误有`ClassNotFoundException`和`InvalidClassException`，前者发生在本地找不到类定义的时候，后者常见于序列化数据和本地类定义的字段类型不兼容
- 因此，为了避免类型定义变动导致的不兼容，Java序列化推荐定义一个特殊的serialVersionUID静态变量，用于表示Java类的序列化版本，如果增加或者修改了字段，就可以改变该UID的值，这样就能自动阻止不匹配的class版本
- Java序列化机制只适用于Java，如果需要和其他语言交换数据的时候，必须使用通用的序列化方法，例如JSON



# 第四章   继承

> 继承也是面向对象的三大特性之一

## Object

> Object是所有类的超类，除了int等基本类型外（interface和enum：没想到吧！！！俺们也是继承自Object！！！）

### Object的方法

- clone
- equals
- hashCode
- toString
- getClass
- waiter
- notify
- notifyAll
- finalize

#### == vs equals

- 对于基本数据类型，== 比较的是数值，对于引用类型，== 比较的是对象的内存地址
- equal用于判断两个对象内容是否相等。继承于Object，如果一般类没有重写该方法，那么其执行效果和== 一致。

#### 重写equals和hashCode

##### 重写equals方法的思想

- 自反性：A.equals(A) == true
- 对称性：A.equals(B)   ->   B.equals(A)
- 传递性：A.equals(B) and B.equals(C)   ->   A.equals(C) == true
- 一致性：只要状态不变，equals不论执行多少次，结果都相同

##### 重写hashCode的思想

- equals()中每一个用于比较的字段，都必须在hashCode()中进行计算
- equals()中没用过的字段，绝对不要放hashCode()中

##### equals和hashCode的关系

- 如果a=b，那么a.equals(b) == true，且 a.hashCode() 必须等于 b.hashCode()
- 如果a!=b，那么a.equals(b) == false，而 a.hashCode() 和 b.hashCode() 尽量不要相等

##### 为什么重写equals的同时必须重写hashCode?

如果不重写hashCode的话，就看会出现a.equals(b) == true，但是a.hashCode() != b.hashCode()的情况，这就很尴尬了，一个HashSet里可能会出现俩相等的东西。因此，要正确使用Map、Set之类的集合，一个自定义对象就必须重写equals和hashCode。

#### 深拷贝与浅拷贝

- 对一个引用对象进行浅拷贝得到的变量与原变量所指向的是同一个对象（只复制了引用）
- 对一个引用对象进行深拷贝得到的变量所指向的是一个新的对象（所有属性也都独立复制了一份新的）

Object.clone()默认为浅拷贝

需要深拷贝，有两种思路：

- 需要深拷贝的类，必须实现Cloneable接口，并重写clone方法，在该方法内部进行深拷贝
- 借助Java的序列化和反序列化进行深拷贝

## 重载与重写

- **重载（overload）**：在同一个类中，方法名相同但方法签名不同，方法签名就是指方法名+参数的数量、类型、顺序。

- **重写（override）**：在子类中，重写父类方法，就是重写。重写的时候也有一些注意事项，比如：方法签名必须相同，子类返回值类型需小于等于父类的返回值，抛出的异常也要小于等于父类，同时访问修饰符大于等于父类（小于在编译时会直接飘红）。

## 多态

> 面向对象的三大特性之一，使得代码更灵活，方便了代码扩展

同一个属性或方法，在父类及其各个子类中，可能会有不同的表现或含义。

Java中的多态，分为编译时多态和运行时多态：

- **编译时多态**：主要通过重载（overload）来实现。在编译时，会进行重载解析，来确定到底该执行重载方法中的那一个。这是静态的多态。

> 也有特殊的重写多态也属于编译时多态：当对象的引用指向的是当前对象自己所属类的对象时，也是编译时多态，因为在编译阶段就能确定执行的方法到底属于哪个对象。

- **运行时多态**：主要通过重写（override）来实现。让子类继承父类并重写父类中已有的方法或者抽象方法。这是动态的多态，也称后绑定。这种就是我们通常说的多态性。

### 多态的实现方式

- 方法重载：根据方法签名的不同，在编译时确定到底执行重载方法中的哪一个
- 方法重写：不同子类对父类某个方法有不同的实现方式
- 接口实现：接口是一种无法被实例化，但可以被继承的抽象类型，是对抽象方法的集合。一个接口可以有多个实现，这也是多态的一种实现形式，与继承中的方法重写类似

## 枚举类 vs 普通类

### 相同点

- 均可实现接口
- enum也是继承自Object

### 不同点

1. 枚举类无法派生子类，它的默认修饰符为final
2. 枚举类的构造方法只能使用private修饰
3. 枚举类所有实例必须在第一行显示给出，否则该枚举类永远都不能产生实例---废话，构造方法都private了
4. 因此，每个枚举值实例在JVM中都是唯一的，可以直接 == 比较！！！2和3造成的连锁反应
5. Enum类还默认提供了一个values方法，可以快速遍历所有枚举值---超有用，由属性快速找到对应枚举实例

## 反射

对于反射有一个通俗的解释，我觉得很形象，就是：Java是一门静态语言，反射则赋予了其动态特性。我理解呢，就是：程序运行的过程一般都是“编码-编译-运行”，而反射正好相反，是在运行过程中反向获取源代码级别的信息。这样可操作的空间其实就很大了。
反射很多地方其实都在不知不觉中被动使用了，比如Spring框架的很多特性都是依赖反射的。我个人主动用的比较多的地方其实主要还是在写单测的时候，可以直接获取我所修改的类。不过有一说一，现在单测肯定不会自己手动写了。。。


# 第五章   接口、lamda表达式与内部类

有一说一，都要2027年了，我已经很久没手动写过这些东西了，真不熟了。。。。
大概过一遍就行了。

## 函数式接口

有且仅有一个抽象方法的接口，就叫函数式接口，最典型的就是Comparator接口了。

```java
@FunctionalInterface   // 有该注解还不报错的，是函数式接口没跑了。但不加这个其实也行。。。
public interface Comparator<T> {
    int compare(T o1, T o2);   // 唯一的抽象方法
    boolean equals(Object obj);   // 就是Object里面的equals方法
    // 默认方法，子类不需要重复实现它
    default Comparator<T> reversed() {
        return Collection.reverseOrder(this);
    }
    // 静态方法
    public static <T extends Comparable<? super T>> Comparator<T> reverseOder() {
        return Collections.reverseOrder();
    }
}
```

## 匿名内部类与Lambda表达式

```java
// 不区分大小写的情况下，保证小写的在前面
Collections.sort(keys, new Comparator<String>() {
	@Override
	public int compare(String o1, String o2) {
		return o1.compareToIgnoreCase(o2) == 0 ? -o1.compareTo(o2) : o1.compareToIgnoreCase(o2);
	}
});

Collections.sort(keys, (o1, o2) -> o1.compareToIgnoreCase(o2) == 0 ? -o1.compareTo(o2) : o1.compareToIgnoreCase(o2));
```

## 内部类

### 内部类的种类

#### 成员内部类

- 成员内部类的实例不能单独存在，必须依附于一个外部类的实例
- 成员内部类可以通过OuterClass.this访问外部类实例的变量和方法，也可以定义自己的成员变量和方法

```java
pubulic class OuterClass {
	private String outerName;
	
	public class InnerClass {
		private String innerName;
		
		public void hello() {
			sout(OuterClass.this.outerName + innerName);
		}
	}
}

OuterClass outer = new OuterClass();
OuterClass.InnerClass inner = outer.new InnerClass();
```

#### 静态内部类

- 静态内部类不再依赖外部类的实例，可以直接直接通过外部类名访问
- 静态内部类无法引用OuterClass.this，但可以访问外部类的静态字段和静态方法

```java
pubulic class OuterClass {
	private static String name;
	
	public class InnerClass {
		public void hello() {
			sout(name);
		}
	}
}

OuterClass.InnerClass inner = new OuterClass.InnerClass();
```

#### 匿名内部类

- 匿名内部类不需要明确地在外部类中定义，可以直接在方法内部，通过匿名类的形式来定义
- 和Lambda表达式作用类似，简化代码

### 匿名内部类和Lambda表达式的区别

- 匿名内部类可以提供接口，也可以是抽象类，以及具体类。Lambda表达式只能是接口
- 如果接口中只包含一个抽象方法，也就是函数式接口，匿名内部类和Lambda表达式都能用，一般逻辑简单的就直接Lambda了，逻辑复杂的最好还是用匿名内部类。但如果接口中多于一个抽象方法，那么只能用匿名内部类了
- 匿名内部类：在编译之后会产生一个单独的.class字节码文件；Lambda表达式：编译的时候不会产生.class文件，对应的字节码会在运行时动态生成

### 为什么要使用内部类？

- **封装性**：定义一个类，不想轻易被任何人访问，咋办捏？因为**一般的顶级类，是不允许被 private 与protected修饰的**，但内部类可以。那就跟封装一个成员变量一样，把它封装在另一个顶级类之中。由顶级类提供方法来访问它，这个方法可以进行一些安全校验，来保护数据
- **实现多继承**：众所周知，Java一个类只能继承一个父类。但我可以有多个内部类啊，我每个内部类特么的继承一个父类，岂不是爽歪歪！
- **简写函数式接口**：匿名内部类可以直接在方法内部定义成实现了函数式接口的类，减少定义类的步骤，虽然Lambda更简洁，但逻辑太复杂的时候匿名内部类还是更有可读性一些
- **解决继承并实现接口时，出现同名方法的问题**：如果一个类的父类，以及它实现的接口中，有同名方法，要怎么区分这个方法是继承来的还是接口的呢？这里可以选择写一个内部类，来实现接口，这样一来，主类调该方法就是父类的方法，内部类调调该方法，就是接口的方法。

# 第六章   异常

## Throwable

`Throwable`是Java异常体系的根，Java所有异常由此衍生，它同样继承自Object。

`Throwable`有两大子类，`Error`和`Exception`。

## Error

`Error`表示严重错误，程序对此一般无能为力

- `OutOfMemory`：OOM，内存耗尽，令人闻风丧胆
- `StackOverflowError`：栈溢出/某个IT网站？

## Exception

`Exception`大多数是可以有程序避免或者解决的，它又分为`RuntimeException`类异常和其他异常两大类

### RuntimeException

一般是由编程错误导致的---`如果出现RuntimeException异常，那一定是你的问题！`

- NullPointerException   使用变量之前怎么不检验它是否为null？
- IndexOutOfBoundsException   就是你小子把数组下标写超了？？
- ArithmeticException   用整数除以0，这是人干出来的事？？？
- ClassCastException   强制转型出错了？？？？建议看看第七章---泛型

### 非RuntimeException

不是RuntimeException，那一定就是非RuntimeException咯。也就是说，程序本身可能没问题，但类似I/O错误造成的异常也是很常见的，需要用程序来解决这样的异常。主要有IOException，ReflectiveOperationException等类。

- FileNotFoundException   使用文件前不知道检查一下文件在不在？额，报一丝，检查的时候还在，用的时候么了。。。但是代码还是可以针对这样的异常进行一些对应的处理的。
- SocketException

## 异常处理原则

- 必须捕获的异常：RuntimeException及其子类除外，所有的Exception及其子类，这种类型的异常称为Checked Exception
- 不需要捕获的异常：Error及其子类，RuntimeException及其子类。

> 注意：编译器对RuntimeException及其子类不做强制捕获要求，不是指程序本身不需要捕获并处理它了。是否需要捕获，以及怎么处理，需要具体问题具体分析。



# 第七章   泛型

## 什么是泛型？为什么要有泛型？

假设，我们现在有一个需求，需要写一个方法，它可以对数组进行排序，要求不论是整型数组，还是浮点型数组、字符串数组等等各种类型的数组都可以用它来排序。怎么搞呢？

- 大聪明A：好说，我会重载啊，每个数据类型我重载一个方法不就行了！ emmm，那如果每多一个自定义类，你又多写一个方法？代码有**可复用性**吗？
- 大聪明B：那也好说，我的方法参数直接用Object[]数组，那不就什么类型都可以处理了！ 好想法，那你就会在Object类型和各种类型直接进行**强制类型转换**，ClassCastException已经盯上你了！

从本质上来讲，泛型就是类型参数化，通过类型参数化，来实现一套代码对多种参数类型进行动态处理，提高了代码**可复用性**；同时，泛型还提供了编译时对类型安全进行检测的机制，可以在编译时就能检测出非法的类型。保证了代码的**安全性**。

## 擦拭法

Java的泛型实现方式就是擦拭法。所谓擦拭法，是指：虚拟机在运行时对泛型其实是一无所知的，编译器会把所有类型变量擦除，并替换为限定类型。在这个过程中，编译器就会对类型安全进行检测。

## 类型转换

Java有两种转型方式：

### 向上转型

将子类对象赋值给父类类型的引用变量，不需要强转转型。但这个时候只能访问父类中定义的方法和属性了。无法访问子类中特有的方法和属性。

```java 
Animal animal = new Dog();
```

### 向下转型

将指向父类类型的引用变量转换为子类类型的引用变量。这样做需要用到强制类型转换操作符`cast`。

``` java
Animal animal = new Dog();
Dog dog = (Dog) animal;
```

向下转型只能在向上转型的基础上进行，因为需要确保animal所引用的对象确实是一个Dog类对象，否则会抛出`ClassCastException`异常。

## extends

使用类似`List<? extends Number>`通配符时，表示：

- 泛型类型限定为Number及其子类

- 可以获取Number：`Number i = list.get(0);` 
- 不可以写数据，如`list.add(new Integer(1))`，编译会报错

即使用`extends`通配符时，可读不可写：

- 可读是因为可以保证List里面放的都是Number的子类，不管是Integer还是Double，都可以**向上转型**成Number
- 不可写是因为Number虽然可以与子类兼容，但子类之间不一定兼容，比如Integer和Double，List<Integer>肯定放不下Double，干脆就不允许往里面放东西了

## super

使用类似`List<? super A>`通配符时表示：

- 泛型类型限定为A及其父类

- 可以写入数据，但只能是A以及A的子类，如：`list.add(A a);`
- 不能获取数据，如：`A a = list.get(0);` 但能获取Object，如：`Object obj = list.get(0);`

即使用`super`的时候，可写不可读：

- 可写是因为A及其子类都可以**向上转型**成A以及A的父类，List<A’sDaddy>，肯定可以放A以及A‘sBaby，这没毛病
- 不可读是因为，你不能将A读成A'sBaby，**向下转型**是不安全的，所以也干脆不让读了

## PECS原则

何时使用`extends`，何时使用`super`？PECS闪亮登场！**Producer Extends Consumer Super**。

- 如果要返回T，则是生产者，要使用`extends`通配符。可以理解成生产者生产A以及A的子类，在用到该方法的地方，肯定是要读输出内容的
- 如果要写入T，那就是消费者，需要使用`super`通配符。可以理解成消费者只能处理A以及A的父类，在用到该方法的地方，肯定是要把内容写给该方法的



# 第八章   集合

## List

### ArrrayList扩容机制

- 底层数组的默认初始容量为10，空数组初始化容量为0，懒加载，会在第一次添加数据时直接扩成10
- 每次扩容后的新容量为**原来的1.5倍**，会调用`Arrays.copyOf()`创建一个新的数组，将旧数组元素进行转移
- 如果扩容后的新容量大于`Integer.MAX_VALUE - 8`，需要二次确认；如果实际所需的容量已经大于该值，就封顶为`Integer.MAXVALUE`
- 若数组长度已经到达`Integer.MAXVALUE`，继续add就会导致int循环溢出为负数，抛出OOM
- 在需要添加大量元素之前，可以调用`ArrayList.ensureCapacity(int minCapacity)`方法，避免底层疯狂`Arrays.copyOf()`扩容

### ArrayList和Vector

`ArrayList`和`Vector`都是`List` 的子类，前者线程不安全，后者通过在每个方法上指定`synchronized`关键字实现线程安全。

### ArrayList和LinkedList

- 是否线程安全：都不安全
- 底层数据结构：前者是Object数组；后者为双向链表，存在头尾指针
-  插入和删除是否收到元素位置的影响：前者如果是在数组中间插入/删除元素，则必须向后/向前移动相应位置之后的所有元素；后者因为是链表结构，只需要定位到对应为止，修改前后节点指针即可。**因此`LinkedList`在插入删除操作上的效率比`ArrayList`高**
- 是否支持随机访问：前者支持，可以通过下标直接访问；后者不支持。**因此`ArrayList`在访问操作上的效率比`LinkedList`高**
- 扩容机制：前者1.5倍扩容，后者不需要扩容

### CopyOnWriteArrayList

`CopyOnWriteArrayList`不是List子类，它是一个同样线程安全，但比`Vector`性能更高的`List`类。

- 相比`Vector`的`synchronized`，`CopyOnWriteArrayList`的所有读操作都是无锁的
- add操作一样使用synchronized关键字加锁，四步走：
  - 加锁
  - 从原数组中拷贝出新数组
  - 在新数组上进行操作，并把新数组赋值给引用变量
  - 解锁
- 除了加锁，`CopyOnWriteArrayList`的底层数组还用了`volatile`关键字修饰，一旦数组被修改完成，其他所有读线程都能立刻感知
- 适合**读多写少**的，需要线程安全的场景
- 用**空间**换取了线程安全

## HashCode

> 在讨论HashMap之前，先特训一下HashCode吧！

```java
// String.hashCode方法
public int hashCode() {
    int h = hash;
    if (h == 0 && value.length > 0) {
        char val[] = value;
        for (int i = 0; i < value.length; i++) {
            h = 31 * h + val[i];
        }
        hash = h;
    }
    return h;
}
```

### 那么问题来了，为什么固定乘积31呢？

- 31是一个奇质数
- `31 * h == (h << 5) - h` 恒成立！位运算远比乘法运算要快，而且JVM也会自动支持这样的运算优化
- 31是经过实战考验的！有大佬测试过10W+单词的散列，固定乘积到31的时候碰撞概率已经非常低了，再大就不礼貌了

## HashMap

### 内部存储结构

- 内部维护了一个`Node`数组`table`，`Node`是一个内部类，它实现了实现了`Entry`接口，维护了hash、key、value以及指向的下一个`Node`，所以`table`数组中每一个单位都可以看做一个Hash Bucket，即Hash桶，里面存放了一个Node列表或者红黑树

  ```java
  static class Node<K, V> implements Map.Entry<K, V> {
  	final int hash;
      final K key;
      V value;
      Node<K, V> next;
  }
  
  transient Node<K,V>[] table;
  ```

- `table`成员变量被transient关键字修饰（不参与序列化），这是因为不同操作系统对同一个对象的哈希计算结果可能是不同的，不能将当前平台上的Hash值用于其他平台。因此，HashMap的序列化做法应该是将所有key进行保存，反序列化时重新生成一个HashMap，并重新计算每个key和Hash值，并将每个Node逐个插入

### 构造方法

- HashMap的构造方法可以传入初始长度和负载因子，不传的话数组的默认初始长度为16，负载因子为0.75，如果手动传入数组长度，初始长度会选择一个刚好大于等于传入参数的，2的幂次数值
- JDK 8采用的是懒惰初始化，仅计算数组的初始长度，会在第一次put的时候resize初始化；而JDK 7则是直接进行了数组创建

### get() 方法

- 首先是找到对应的Bucket

  - 计算key的Hash值：
    - 这里先使用Object.hashCode()方法获取key的Hash原值，通常是32位，太大啦，所以会使用一个扰动函数
    - 具体操作就是：原Hash值右移16位之后，剩下高16位，和原Hash值做异或运算，这就是**扰动函数**
    - 相当于把高16位信息揉进了低16位中，低位的散列效果会更好。为啥捏？

  - 因为接下来结算Bucket位置时，会拿`table的长度 - 1`和刚刚计算出来的Hash值与一下。这里table长度减一就全是11111了，与操作就相当于取模，得到的结果就是Bucket位置了。可以看出来，如果table长度不是特别长，那1就比较少，做与运算是基本上都是Hash值的低位参与，这个时候就提现出**扰动函数**的重要性了！

```java
// 异或Hash值的高16位和低16位的操作，被称为扰动函数，增加随机性，减少碰撞
int hash = (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
// table长度减1的二进制全是1，所以直接&运算非常方便
Node<K,V> first = tab[(tab.length - 1) & hash];
```

- 之后，再遍历Bucket里的列表/红黑树找到对应的Node

### put() 方法

1. 先通过扰动函数计算出key的新Hash值
2. 判断table是否为空，或者长度为0，如果是则进行resize初始化操作
3. 找到Bucket位置
   - 若当前桶里无数据，那就直接插入，size++
   - 如果当前Bucket的首位key正好是我们要存放的key，那就覆盖
   - 否则就需要遍历Bucket里的链表或红黑树了
4. 判断当前Bucket里是否是红黑树：
   - 如果是链表，那就在链表中插入/覆盖节点
   - 如果是树，向树中插入/覆盖节点
5. 如果链表中插入节点后，链表长度大于等于8，则需要把链表转红黑树
   - 链表转树方法为`treeifyBin`
   - 不是所有链表长度达到8的时候都会转成树，还需要判断table长度是否大于64，如果小于64，就会优先选择扩容，扩容之后，该Bucket里的链表长度就小于8了
6. 数据放进去之后，判断有size是否超过阈值`threshold`，超过则resize扩容

![HashMap的put方法](pics/HashMap的put方法.webp)

### 扩容机制

> 当table里有数据的Bucket数量超过`table长度 * 负载因子`时，就需要扩容了

#### 为什么默认的负载因子=0.75

- 源码中对此作了解释：作为一般规则，0.75在时间和空间成本上提供了很好的折中。较高的值会降低空间开销，但会相应地增加碰撞概率，提高查找成本。设置初始值大小时，需要考虑预计的Bucket数及其负载数，并尽量减少`resize`操作的次数。如果初始容量大于`数据最大长度*负载因子`，`resize`操作就不会发生了
- 当然，还有数学解释。有大佬认为，一个Bucket空和非空的概率分别为0.5，那么通过概率统计学计算出来负载因子的值为 `log(2) ≈ 0.693`，大佬认为任何小于0.75，大于0.693的值都可以提供很好的性能，0.75可能就是随便选的

#### resize() 方法

- 对原数组大小和扩容阈值进行判断，如果数组容量超过`(1 << 30)`，则不再进行扩容了，任由元素进行碰撞
- 按照新数组的大小初始化一个新的table，旧数组由oldTab持有，判断oldTable是否为空，若为空，则说明是第一次初始化操作，直接返回新table即可
- 如果不是初始化，那就要对旧数据进行迁移操作了。根据节点Hash值和新table大小重新取模，得到各个Node在新数组中的具体位置。如果是独立头节点，则直接进行迁移操作；如果是树节点，则需要将红黑树拆分成两个子链表迁移，再分别按需转红黑树；如果是链表头节点，则需要对链表进行拆分
- JDK 8中，链表拆分性能提升巨大：
  - 每个Node都有自己的Hash值属性，不需要重新计算
  - 新table长度为旧的两倍，也就是说二进制就在最右边多了一位1,
  - 看Node.getHash()在该位置上的值
    - 为0，则原位置
    - 为1，则放新位置
  - 所以，就是先把每个Bucket中的链表按上述方法分成两个链表，一串留在原位，一串放新位置
- JDK 7中，该操作是每拿到一个Node，就直接插到新数组中效率要低很多

### 为什么链表转红黑树的阈值为8？

- 源码中对此也做出了解释，Hash函数设计良好的情况下，一个Bucket中元素个数要达到8的概率是千万分之一！所以8就够了，再大就不礼貌了。反之如果链表长度还不到8，硬是要转成红黑树的话，反而不如链表的效率。
- 所以，上当我们使用HashMap时，如果真出现了红黑树结构，这恰恰说明我们对象的hashCode方法实现得不好，容易出现冲突，要及时改进
- 红黑树的节点是普通节点的两倍大小，尽量少用呢。它是一种**保底策略**，**保证极端情况下查询的效率**

### remove() 方法

- 先找到Bucket位置，再用equals进行比较，确定节点位置
- 如果是头节点，那就删除后将下一个节点放上来，下一个节点可能为空
- 如果是链表节点，那就正常地删除该节点
- 如果是红黑树，就用红黑树的方式删除节点
- 如果红黑树删除节点后，大小小于等于6，则退化成链表。为啥不是8了呢？因为防止某个大小为7/8的Bucket，在链表和红黑树之间反复横跳

### 为啥用红黑树而不是AVL树

- 因为平衡树要求每个节点的左子树和右子树的高度差最大为1，这个要求实在太严了，导致每次进行插入/删除节点的时候，几乎都会破坏平衡树的规则，进而需要通过左旋和右旋来进行调整，让它重新平衡
- 红黑树则使用**非严格的平衡**来换取增删节点时候选择次数的降低。而且对红黑树来说，任何不平衡都会在三次选择之内解决，相较于AVL树为了维持平衡所需的开销，要小很多。因此红黑树的插入效率也相对更高
- 单单在查找方面比较效率的话，由于AVL树高度平衡，因此AVL树的查找效率要比红黑树更高
- 实际应用中，若搜索的频率远远大于插入和删除的话，那就选择AVL；如果两者频率差不太多，那就选红黑树

### HashMap的线程不安全

HashMap的线程不安全主要体现在：死循环、数据丢失、数据覆盖等问题。其中死循环和数据丢失在JDK8中已得到解决，因为**插入方式从头插法改成了尾插法**。然而JDK8中，在并发执行HashMap的put方法时，仍然会有数据覆盖的问题。

#### HashMap的死循环和数据丢失

简单来说，就是一个线程准备扩容并迁移节点时，被挂起了。此时另一个线程完成了扩容以及迁移操作，导致前一个线程先前拿到的节点信息发生了变化。这个时候老线程再用头插法进行数据迁移，因为头插法会反转链表顺序，就可能导致新数组上的链表成环，以及数据丢失。

#### HashMap的数据覆盖问题

- 假设A、B两个线程都在进行put操作，并且元素插入的Bucket位置是相同的。当A找到元素需要插入的位置时，由于时间片被耗尽导致挂起，而B得到时间片后在该Bucket中插入了元素。当线程A又重新获得了时间片，由于之前已经找到了元素要插入的位置，所以此时不会再进行计算，而是直接进行插入，这就导致了线程B插入的数据被线程A覆盖了，导致线程不安全
- 假设A、B两个线程都在进行put操作，并且元素插入的Bucket位置是不同的。当A完成插入元素的操作后，从主存中获取了`size`并准备执行`++size`，但又特么由于时间片被耗尽导致挂起了。这个时候B线程也从主存中获取了获取了`size`并完成了`++size`，写回了主存。当线程A又重新获得了时间片，**由于size变量不是由volatile修饰的**，它会继续使用自己工作内存中的`size`，`++size`并写回主存。最终，A、B各插入了一个元素，但`size`只加了1，这也是线程不安全

## HashTable

- 线程是否安全：HashTable使用synchronized关键字修饰操作方法来获得相对线程安全
- 对null键的支持：HashTable不支持null键
- 初始容量：HashTable的默认初始容量为11，而且会直接使用手动传入的容量作为初始容量
- 扩容：每次扩容，都为原来的2n+1

## LinkedHashMap

在HashMap的基础上，增加了双向链表结构，LinkedHashMap可以维护插入顺序或者LRU顺序。

它维护了头尾指针`head`和`tail`，然后有一个`accessOrder`属性来控制是按照插入顺序还是LRU顺序，默认为`false`，插入顺序。

## TreeMap

- TreeMap可以对key进行排序
- TreeMap底层是一个`Entry<K, V> root`，实现结构是一棵红黑树
- HashMap底层是数组，因此在冲突不严重的情况下，查找、添加、删除都比TreeMap快
- TreeMap在添加或删除元素时，会进行排序，从而影响性能

## ConcurrentHashMap

- ConcurrentHashMap也是一个线程安全的Map，但相比于HashTable一句话不说直接上synchronized，ConcurrentHashMap效率要高不少。
- 在JDK7中，维护了一个Segment数组，每个Segment对应一个Entry数组和一把ReentranLock锁。也就是说维护了一个分段锁，不同线程访问不同Segment，不会造成冲突，提高了并发度
- 在JDK8中，改用CAS和Bucket来实现了，细化了锁的粒度。在插入的时候先用CAS判断该节点是否有Hash冲突，没有的话直接插入，有的话才用synchronized上锁。提高了效率

### get() 方法没上锁，咋保证读取的不是脏数据？

ConcurrentHashMap中`Node`节点的`val`和`next`成员属性都是用了`volatile`修饰。
