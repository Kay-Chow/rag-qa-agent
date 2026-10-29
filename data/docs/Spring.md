# Spring和Spring Boot的关系

Spring是一个开源框架，也是现在Java开发的行业标准。Spring全家桶提供了非常多的组件供我们使用，包括Spring MVC，Spring Data，Spring Cloud和Spring Boot等。

Spring Boot是一个基于Spring的套件，它帮我们预装了Spring的一系列组件，以便用尽可能少的代码和配置来开发基于Spring的Java应用程序。

以汽车为例，如果我们想组装一辆汽车，我们需要发动机、传动、轮胎、底盘、外壳、座椅等各种部件，然后把他们装配起来。Spring就相当于提供了一系列这样的部件，但是要装好汽车上路，还需要我们自己动手。而Spring Boot则相当于已经帮我们预装好了一辆可以上路的汽车，如果有特殊的需求，例如把发动机从3缸发动机换成V8发动机，可以通过修改配置或者编写少量代码完成。

因此，Spring Boot和Spring的关系就是整车和零部件的关系，他们不是取代关系。Spring Boot的目标就是提供一个开箱即用的应用程序架构，我们基于Spring Boot的预置结构继续开发，省时省力。

# Spring Boot的自动装配原理

Spring Boot项目启动时，会从所有的`META-INF/spring.factories`文件中读取一系列的组件名称导入到容器当中，其中最主要的是位于`spring-boot-autoconfigure-x.x.x.jar`包下的`spring.factories`文件，它包含了所有Spring Boot帮助我们进行自动配置的自动配置类**全限定类名**，这些自动配置类都是由该包自己提供的。

总而言之，就是规定好文件的具体路径和名称，然后再其中写死所有需要的自动配置类名称，Spring Boot就会根据这些**全限定类名**，到对应的包下进行类的加载。**其实就是SPI机制的实现。**

虽然会读到很多的自动配置类，并且这些自动配置类有又各自包含了许多组件，但是得益于`@Conditional`注解所提供的条件装配功能，可以非常方便地按需开启自动配置。

# IoC （Inversion of Control)

## IoC思想

IoC，就是控制反转，是一种软件设计原则，将创建对象的控制权进行反转。

传统应用中，对象都是由开发者手动创建，并维护的。如果一个系统有大量的对象，同时对象间的相互依赖关系错综复杂。那么：

1. 要怎么根据依赖关系合理创建对象？
2. 销毁时，又如何按依赖顺序正确销毁组件？

还要由开发者自己来维护的话，有点强人所难了。那么，解决这一系列问题的核心方案就是IoC。

Spring的核心就是提供了一个IoC容器，在IoC容器中，开发者不需要再自己创建对象，IoC容器会根据需求自动创建所需要的对象，并负责管理对象的声明周期。

## IoC实现方式

> IoC还有另一个名称：依赖注入，可以由它的实现方式来引申。

- 最原始的XML文件配置：将bean的配置写在XML文件中，由IoC扫描XML文件，并装配bean
- 基于注解：
  - 写一个配置类，在配置类中实现bean的构造方法，由IoC扫描配置类，并装配bean
  - 直接装配bean，在bean上添加@Component注解，由IoC扫包，直接装配bean
- **创建了很多Bean之后，怎么解决对象之间错综复杂去的依赖关系呢？**直接使用@Autowire、@Qualifier等注解，就能实现依赖对象的注入。

# AOP （Aspect Oriented Programming）

面向切面编程，是一种抽象化的面向对象编程。

对于安全检查、日志、事务等代码，它们会重复出现在每个业务方法中。而AOP就是把这些重复的、非业务的代码抽离出来，作为切面，织入到核心逻辑中，实现Proxy模式。

# Spring MVC

## MVC流程

1. 客户端（浏览器）发送请求，直接请求到`DispatherServlet`
2. `DispatherServlet`根据请求信息调用`HandlerMapping`，解析请求对应的`Handler`
3. 解析到对应的`Handler`（也就是`Controller`），开始由`HandlerAdapter`适配器处理
4. `HandlerAdapter`会根据`Handler`调用真正的处理器开始处理请求，并处理相应的业务逻辑
5. 处理器完成业务后，会返回一个`ModelAndView`对象，`Model`是返回的数据，`View`是一个逻辑上的`View`
6. `ViewResolver`会根据逻辑`View`查找实际的`View`
7. `DispatcherServlet`会把返回的`Model`传给`View`（视图渲染）
8. 把`View`返回给请求者

# Bean的生命周期

- 生产
  - `loadBeanDefinitions`：**通过XML、注解扫描等方式，将定义好的Bean一个个都找到**，并放入`beanDefinitionMap`中
  - `createBean`：遍历`beanDefinitionMap`，一个个create
    - `createBeanInstance`**（构造对象）**：通过反射机制，从`beanDefinition`中的`beanClass`拿到类的构造方法
    - `populateBean`**（填充属性）**：对Bean内部的属性进行填充，通常就是带`@Autowired`的变量，进行依赖注入
    - `initializeBean`**（初始化实例）**：
      - `invokeAwareMethods`（执行信息感知方法）：初始化容器相关信息，为实现了各种Aware接口的Bean设置`beanName`，`beanFactory`等容器信息，目的是为了让Bean能够感知到自己的这些属性
      - `invokeInitMethods`（执行初始化方法）：主要执行程序员自定义的`initMethod`方法
        - 在`invokeInitMethods`前后，分别进行`applyBeanPostProcessorsBeforeInitialization`和`applyBeanPostProcessorsAfterInitialization`方法，处理各种Bean的后置处理器，还包括我们的负责AOP的处理器：`AnnotationAwareAspectJAutoProxyCreator`，以及负责Bean构造后`@PostConstruct`和销毁前`@PreDestroy`的处理器等
    - `registerDisposableBean`**（注册销毁）**：将实现了销毁接口`DisposableBean`的Bean进行注册，这样在销毁Bean的时候就能直接执行`destroy`方法了
  - `addSingleton`：**将create好的Bean放入单例池**`singletonObjects`中就可以被获取和使用了
- 使用：直接从单例池获取，所以，**所有的Bean都是单例模式~**
- 销毁
  - `postProcessBeforeDestruction`（销毁前处理器）：处理销毁前的逻辑
  - `destroyBeans`**（销毁Bean对象）**：执行生产时销毁注册过的Bean的`destroy`方法
  - `invokeCustomDestroyMethod`（执行自定义销毁方法）：执行我们自己定义的销毁方法

# SpringBoot的启动流程

> 一般是由加了@SpringBootApplication注解的启动类来启动。

- 服务构建-SpringApplication初始化构造
  - 首先读取资源加载器、主方法类
  - 然后确定web服务类型，默认为Sevlet服务，如Tomcat，还有Reactive
  - 读取所有META-INF/spring.factories文件中的注册初始化、上下文初始化和监听器配置
  - 获取启动类
- 环境准备-调用run方法
  - 注册初始化
  - 启动运行监听器，这里会启动服务化构建时读取的所有监听器，这里监听器使用了观察者模式，逐一串联执行。并发布”启动“事件
  - 组装启动参数，加载环境变量。并发布”环境准备完成“事件
  - 打印Banner图！！！很帅！！！
- 容器创建-ApplicationContext
  - 创建beanFactory，用于存放和生产Bean
  - 创建后处理器
    - ConfigurationClassPostProcessor：用于解析@Component、@ComponentScan等注解
    - AutowiredAnnotationBeanPostProcessor：用于解析@Autowired、@Value、@Inject等
    - CommonAnnotationBeanPostProcessor：
  - prepareContext对容器中的部分属性进行初始化
    - 上下文初始化，容器ID、警告日志处理、日志监听，都是在这里实现的
    -  发布“容器准备完成”监听事件
    - 为容器注册启动参数、Banner、懒加载策略等
    - 将Bean定义加载到beanDefinitionMap中
    - 发布“资源加载完成”事件
- 填充容器-自动装配
  - 生产所有Bean
  - 填充到容器中
