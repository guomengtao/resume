---
# 精简Spring Boot项目目录结构

```
src/
 └─ main/
     ├─ java/
     │    └─ com/
     │        └─ yourpackage/
     │             ├─ controller/
     │             │    └─ CustomerController.java   # 提供REST接口
     │             ├─ entity/
     │             │    └─ Customer.java             # 实体类，定义数据模型
     │             ├─ repository/
     │             │    └─ CustomerRepository.java   # 数据访问层接口
     │             └─ service/
     │                  └─ CustomerService.java      # 业务逻辑层
     └─ resources/
          ├─ application.properties                   # 配置文件
          └─ data.sql                                 # 初始化数据（可选）
```

## 目录作用说明

- **controller**：处理请求，调用服务层，实现接口逻辑  
- **entity**：实体类，映射数据库表  
- **repository**：继承Spring Data JPA接口，负责数据存取  
- **service**：封装业务逻辑  
- **resources/application.properties**：配置数据库连接及其他参数  
- **resources/data.sql**：启动时初始化数据库数据（可选）

---

## 项目目录结构示意图（Mermaid）

```mermaid
graph TD
    A[src/main/java/com/yourpackage] --> B[controller]
    A --> C[entity]
    A --> D[repository]
    A --> E[service]
    F[src/main/resources] --> G[application.properties]
    F --> H[data.sql (optional)]

    B --> I[CustomerController.java]
    C --> J[Customer.java]
    D --> K[CustomerRepository.java]
    E --> L[CustomerService.java]
```