def get_wrong_reason(idx,path,now_problem_info,problem_id_now,input_format_requirement,explanation11,explanation22,max_x):
    result = subprocess.run(['python3', './problems/' + problem_id_now + '/' + 'judge.py','--code_path','code_fan_'+str(idx)+'.py'], capture_output=True,text=True)
    time.sleep(3)
    with open(path + "/first_python_results.json", "r", encoding="utf-8") as json_file:
        now_first_result = json.load(json_file)
    error_message = now_first_result['message']
    match = re.search(r'样例：\n(.*?)\n', error_message)
    try:
        input3 = int(match.group(1))
    except:
        input3 = "There are no specific sample inputs, and the program itself has an error:" +error_message
    output3 = ""
    if input3 == "There are no specific sample inputs, and the program itself has an error:" +error_message:
        output3 = "There are no specific sample outputs"
    else:
        for i in range(len(now_problem_info['test'])):
            tmp_d = now_problem_info['test'][i]
            if tmp_d['input'] == input3:
                output3 = tmp_d['output']
                break
    try:
        assert output3 != ""
    except:
        pdb.set_trace()

    code_now = ""
    with open(path + '/code_fan_' + str(idx) + '.py', 'r', encoding='utf-8') as file:
        code_now = file.read()
    assert code_now != ""

    if idx != 0:
        code_next = ""
        with open(path + '/code_fan_' + str(idx-1) + '.py', 'r', encoding='utf-8') as file:
            code_next = file.read()
        assert code_next != ""
    else:
        code_next = ""
        with open(path + '/code.py', 'r', encoding='utf-8') as file:
            code_next = file.read()
        assert code_next != ""


    if idx > 1: 
        cnt_try = 0
        f = 1
        while True:
            if cnt_try > 1:
                f = 0
                break
            try:
                cnt_try += 1
                prompt3 = copy.deepcopy(gaixie_code).format(origin_code=code_next,
                                                            json_format='''{"function":"xxx","rewrite_code":"xxx"}''')
                code_next = generate_one(prompt3, temp=1, model_name='deepseek-chat')
                code_next = code_next[code_next.find('{'):code_next.rfind('}') + 1]
                code_next = json.loads(code_next)['rewrite_code']
                break
            except:
                continue

    prompt1 = copy.deepcopy(python_error_prompt)
    prompt1 = prompt1.format(problem=now_problem_info['description'],
                            input_format=input_format_requirement,
                            output_format=now_problem_info['output requirement'],
                            input1=now_problem_info['example'][0]['input'],
                            input2=now_problem_info['example'][1]['input'],
                            example_reason1=explanation11,
                            output1=now_problem_info['example'][0]['output'],
                            output2=now_problem_info['example'][1]['output'],
                            example_reason2=explanation22,
                            code=code_now,
                            input3=input3,
                            output3=output3,
                            code2=code_next,
                            json_type='''{"work_reason":xxx,"wrong_reason":xxx}''',
                            ).strip()
    cnt_try = 0
    f = 1
    while True:
        if cnt_try > 1:
            f = 0
            break
        try:
            cnt_try += 1
            pre_analyse = generate_one(prompt1, temp=1, model_name='deepseek-chat')
            pre_analyse = pre_analyse[pre_analyse.find('{'):pre_analyse.rfind('}') + 1]
            pre_analyse = json.loads(pre_analyse)
            break
        except:
            continue
    assert 'work_reason' and 'wrong_reason' in pre_analyse.keys()
    return input3,output3,pre_analyse,code_next

def generate_final_sample(vis,target_folders,origin_data_dict):
    for path in target_folders:
        problem_id_now = path[path.rfind('/') + 1:]
        if problem_id_now in vis:
            continue

        print("--------------------------")
        print(problem_id_now)
        print("------")

        now_problem_info = origin_data_dict[problem_id_now]

        input_format_requirement = generate_one(
            copy.deepcopy(input_re_change_prompt ).format(juzi=now_problem_info['input requirement']), temp=1,
            model_name='deepseek-chat')
        
        explanation11 = generate_one(copy.deepcopy(trans_prompt).format(content=now_problem_info['example'][0]['process1']), temp=1,model_name='deepseek-chat')
        explanation22 = generate_one(copy.deepcopy(trans_prompt).format(content=now_problem_info['example'][1]['process2']), temp=1,model_name='deepseek-chat')
        
        cnt = 0
        for gaixie_cishu in range(5):
            problem_description_now = generate_one(copy.deepcopy(gaixie_timu).format(problem=now_problem_info['description']),temp=1,model_name='deepseek-chat')
            sample_input_string = copy.deepcopy(data_input).format(
                    problem_description=problem_description_now,
                    input_format=input_format_requirement,
                    output_format=now_problem_info['output requirement'],
                    input1=now_problem_info['example'][0]['input'],
                    output1 = now_problem_info['example'][0]['output'],
                    explanation1=explanation11,
                    input2=now_problem_info['example'][1]['input'],
                    output2=now_problem_info['example'][1]['output'],
                    explanation2=explanation22,
                    json_type='''{"cot":xxx,"code":xxx}'''
                    )
            # print(sample_input_string)
            for gaixie_cishu2 in range(4):
                cnt += 1
                f=open(path+'/sample_input'+str(cnt)+'.txt','w',encoding='utf-8')
                f.write(sample_input_string)
                f.close()

                max_x = -2
                for filename in os.listdir(path):
                    # 使用正则表达式匹配符合格式的文件名
                    match = re.match(r'code_fan_(\d+)\.py', filename)
                    if match != None:
                        x = int(match.group(1))  # 提取数字部分
                        max_x = max(max_x, x)  # 更新最大值
                assert max_x != -2

                code_ini = ""
                with open(path + '/code_fan_'+str(max_x)+'.py', 'r', encoding='utf-8') as file:
                    code_ini = file.read()
                assert code_ini != ""

                sample_output_string = '''The Python code for this algorithm problem, based on my initial thoughts, is: \n''' + code_ini

                # if max_x == 0:
                #     result = subprocess.run(['python3', './problems/' + problem_id_now + '/' + 'judge.py','--code_path','code.py'], capture_output=True,
                #                             text=True)
                #     assert result.returncode == 1
                #     with open(path + "/first_python_results.json", "r", encoding="utf-8") as json_file:
                #             now_first_result = json.load(json_file)
                #     assert now_first_result["status"] == 1
                #     sample_output_string += "\n\n"
                #     sample_output_string += random.choice(["This code passes all the test cases, so it is the correct solution.","I tested all the examples, and they all passed with this code.","I ran through all the examples, and they all passed the test with this code","This code successfully passes every test case, making it the correct solution.","I can't find any counterexample that would cause this code to fail.","No counterexample exists that would cause this code to fail."])
                #     # print(sample_output_string)
                #     f = open(path + '/sample_output'+str(cnt)+'.txt', 'w', encoding='utf-8')
                #     f.write(str({"cot":sample_output_string,"code":code_ini}))
                #     f.close()
                #     continue

                # input3,output3,pre_analyse,code_next = get_wrong_reason(0,path,now_problem_info,problem_id_now,input_format_requirement,explanation11,explanation22,max_x)
                # sample_output_string += "\n\n"
                # sample_output_string += copy.deepcopy(one_example_cot_format).format(input=str(input3),
                #                                                                         output=str(output3),
                #                                                                         work_reason=pre_analyse['work_reason'],
                #                                                                         error_reason=pre_analyse['wrong_reason'],
                #                                                                         revise_code=code_next)


                for idx in range(max_x,-1,-1):
                    result = subprocess.run(['python3', './problems/' + problem_id_now + '/' + 'judge.py','--code_path','code_fan_'+str(idx)+'.py'], capture_output=True,text=True)
                    time.sleep(3)
                    if result.returncode == 1:
                        code_now = ""
                        with open(path + '/code_fan_' + str(idx) + '.py', 'r', encoding='utf-8') as file:
                            code_now = file.read()
                        assert code_now != ""
                        with open(path + "/first_python_results.json", "r", encoding="utf-8") as json_file:
                            now_first_result = json.load(json_file)
                        assert now_first_result["status"] == 1

                        sample_output_string += "\n\n"
                        sample_output_string += "This code passes all the test cases, so it is the correct solution."
                        # print(sample_output_string)
                        f = open(path + '/sample_output'+str(cnt)+'.txt', 'w', encoding='utf-8')
                        f.write(str({"cot":sample_output_string,"code":code_now}))
                        f.close()
                        break

                    input3,output3,pre_analyse,code_next = get_wrong_reason(idx,path,now_problem_info,problem_id_now,input_format_requirement,explanation11,explanation22,max_x)


                    sample_output_string += "\n\n"
                    sample_output_string += copy.deepcopy(one_example_cot_format).format(input=str(input3),
                                                                                        output=str(output3),
                                                                                        work_reason=pre_analyse['work_reason'],
                                                                                        error_reason=pre_analyse['wrong_reason'],
                                                                                        revise_code=code_next)
                    if idx == 0:
                        result = subprocess.run(['python3', './problems/' + problem_id_now + '/' + 'judge.py','--code_path','code.py'], capture_output=True,text=True)
                        assert result.returncode == 1
                        code_now = ""
                        with open(path + '/code.py', 'r', encoding='utf-8') as file:
                            code_now = file.read()
                        assert code_now != ""
                        with open(path + "/first_python_results.json", "r", encoding="utf-8") as json_file:
                            now_first_result = json.load(json_file)
                        assert now_first_result["status"] == 1

                        sample_output_string += "\n\n"
                        sample_output_string += "This code passes all the test cases, so it is the correct solution."
                        # print(sample_output_string)
                        f = open(path + '/sample_output'+str(cnt)+'.txt', 'w', encoding='utf-8')
                        f.write(str({"cot":sample_output_string,"code":code_now}))
                        f.close()
                        break
