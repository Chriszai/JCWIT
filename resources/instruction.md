首先我们要确定的是我们整个验证还是得围绕witness展开，没有witness意味着什么都干不成，那么如果有并且完整，那么就应该能够成功完成验证。

任何random类函数包括获取当前时间毫秒数都不无法正常显示

---------------------------------------------------------------------------------------------
有可能witness中包含了虚假的属性状态(错误的状态)，或者部分被遗漏的冲突属性并没有被包含在witness中。

执行顺序不一致 性质就不可能匹配  
执行顺序一致，性质可能匹配

1. 首先应该过滤witness 因为witness中包含了很多没有任何信息的孤立的node，以及检查畸形 XML 字符串
2. 验证witness完整性和连接性是否正确，对witness节点和边进行检查。
3. 验证与实际代码的一致性
    Validator会根据Witness中描述的执行轨迹或状态序列来验证程序的执行。查看真实运行轨迹与witness描述的是否一致，并在每个状态上检查程序的行为是否与Witness中描述的一致。
4. 检查性质匹配:
    Validator会检查Witness中描述的性质是否与用户定义的正确性属性相匹配。这可能包括检查性质的类型、范围和约束条件等。例如，如果用户定义了一个不变量，Validator会检查Witness中是否描述了违反该不变量的情况。

witness中的执行顺序和节点状态与java文件中一致只能证明witness中并没有包含虚假的属性状态或错误的运行轨迹，但可能部分被遗漏的冲突属性并没有被包含在witness中。 这也就是为什么最后我们不是简单对比属性是否匹配，而需要通过一个有界模型检查器进行验证。
所以可以确定的是无论如何需要使用jbmc！！！ 那么接下来无论如何就是需要根据witness中的内容修改原有java文件

我们使用ast就是为了不再使用原始文件进行验证，如果还要使用原始文件来给抽象语法树加行号的话，那么用抽象语法树的意义是什么呢？ 所以不能用

                #     java_variable_info = {
                #         "type": matches[0],
                #         "value": value,
                #         "row": row,
                #     }
                #     search_result = re.search(
                #         r"(\d+\.\d+)", java_variable_info["value"]
                #     )
                #     java_variable_info["value"] = (
                #         int(java_variable_info["value"])
                #         if search_result is None
                #         else float(java_variable_info["value"])
                #     )
                #     if self.__variable_property_match(
                #         java_variable_info, witness_variable_info
                #     ):
                #         is_variable_matched = True
                #         break
