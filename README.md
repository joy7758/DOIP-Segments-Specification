# DOIP Segments Specification
# DOIP 分段规范

## Bilingual Governance Notice

## Standard Domain Entry / 标准域入口

- Standard ID / 标准编号：`RR-DOIP`
- Registry Row / 注册表定位：https://github.com/joy7758/RedRock-Constitution/blob/main/docs/registry/STANDARDS_REGISTRY.md#rr-doip
- Hub / 总入口：https://github.com/joy7758/RedRock-Constitution

**CN**: 所有标准文档均以中文与英文同步发布，英文为完整翻译版本。  
**EN**: All standards are published in Chinese and English, and the English content must be a full translation.

## Overview / 概述

Following the **DIGITAL OBJECT INTERFACE PROTOCOL SPECIFICATION VERSION 2.0 (NOVEMBER 12, 2018)**, this repository hosts the Json Schema Objects for validating the segments described in the specification.

遵循 **数字对象接口协议规范 2.0 版（2018 年 11 月 12 日）**，本仓库托管了用于验证规范中描述的分段的 Json 模式对象。

Please refer to [DOIPv2Spec](https://www.dona.net/sites/default/files/2018-11/DOIPv2Spec_1.pdf) or use the [PID](http://hdl.handle.net/0.100/DO-IRPV3.0).

请参阅 [DOIPv2Spec](https://www.dona.net/sites/default/files/2018-11/DOIPv2Spec_1.pdf) 或使用 [PID](http://hdl.handle.net/0.100/DO-IRPV3.0)。

The specification includes the following basic operations: hello, create, access, update, delete, search, and listOperations.

该规范包括以下基本操作：hello, create, access, update, delete, search, 和 listOperations。

## Structure / 结构

- **`doip-request-segments` & `doip-response-segments`**: Contain the request and response segments for the DOIP basic operations (Hello, Create, Retrieve, Update, Delete, Search, and ListOperations).
包含 DOIP 基本操作（Hello, Create, Retrieve, Update, Delete, Search 和 ListOperations）的请求和响应分段。

- **`doip_do_serialization`**: Contains the JSON schema for a serialized DO.
包含序列化 DO 的 JSON 模式。

- **`doip-ex-request-segments` & `doip-ex-response-segments`**: Contain the request and response segments for two extended operations: **Extended-Create** and **Extended-Update**. Those operations have the same effect as the basic Create and Update operations, except that the type-value-pairs that should be written into the PID record by the repository are specified in the respective request/response schema.
包含两个扩展操作的请求和响应分段：**Extended-Create** 和 **Extended-Update**。这些操作与基本的 Create 和 Update 操作效果相同，但由仓库写入 PID 记录的类型-值对在各自的请求/响应模式中指定。

- **Other Operations**: Further extended Operations such as `Op.CreateFDO` can be added following the naming convention.
其他操作：可以按照命名约定添加进一步的扩展操作，例如 `Op.CreateFDO`。

## Work in Progress / 进行中的工作

- Other serialization next to json will be created and uploaded.
将创建并上传除 JSON 之外的其他序列化格式。
- The segments might be registered in the [type registry](https://typeregistry.lab.pidconsortium.net) and the Json schemas will then be derived from those definitions.
这些分段可能会在 [类型注册表](https://typeregistry.lab.pidconsortium.net) 中注册，届时 JSON 模式将源自这些定义。

---

## Belongs to RedRock Constitution / 隶属于红岩宪章体系

This repository is part of the RedRock Constitution architecture framework.

Please start from the central governance hub:

https://github.com/joy7758/RedRock-Constitution

本仓库属于红岩宪章体系，请从总入口开始阅读与理解：

https://github.com/joy7758/RedRock-Constitution

---

## Standard Domain / 标准域

This repository implements Standard Domain `RR-DOIP` under the RedRock Constitution framework.

本仓库实现红岩宪章标准域：`RR-DOIP`

Central Governance Hub:
https://github.com/joy7758/RedRock-Constitution

## Onepager / 一页纸

- `RR-DOIP` Onepager / 一页纸：`docs/onepager/RR-DOIP_ONEPAGER_CN_EN.md`
- Hub / 总入口：https://github.com/joy7758/RedRock-Constitution
