# ['A019705','A032970','A061372','A134906','A171934','A295363','A304906','A360411']
def generate_final_sample(vis,target_folders,origin_data_dict):
    for path in target_folders:
        problem_id_now = path[path.rfind('/') + 1:]
        if problem_id_now not in ['A019705','A032970','A061372','A134906','A171934','A295363','A304906','A360411']:
            continue
        print("--------------------------")
        print(problem_id_now)
        print("------")
        if problem_id_now in vis:
            continue

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

                code_ini = ""
                with open(path + '/code.py', 'r', encoding='utf-8') as file:
                    code_ini = file.read()
                assert code_ini != ""

                sample_output_string = '''The Python code for this algorithm problem, based on my initial thoughts, is: \n''' + code_ini

                max_x = 0
                for filename in os.listdir(path):
                    # 使用正则表达式匹配符合格式的文件名
                    match = re.match(r'code(\d+)\.py', filename)
                    if match != None:
                        x = int(match.group(1))  # 提取数字部分
                        max_x = max(max_x, x)  # 更新最大值
                # print(max_x)

                if max_x == 0:
                    result = subprocess.run(['python3', './problems/' + problem_id_now + '/' + 'judge.py','--code_path','code.py'], capture_output=True,
                                            text=True)
                    assert result.returncode == 1
                    with open(path + "/first_python_results.json", "r", encoding="utf-8") as json_file:
                            now_first_result = json.load(json_file)
                    assert now_first_result["status"] == 1
                    sample_output_string += "\n\n"
                    sample_output_string += random.choice(["This code passes all the test cases, so it is the correct solution.","I tested all the examples, and they all passed with this code.","I ran through all the examples, and they all passed the test with this code","This code successfully passes every test case, making it the correct solution.","I can't find any counterexample that would cause this code to fail.","No counterexample exists that would cause this code to fail."])
                    # print(sample_output_string)
                    f = open(path + '/sample_output'+str(cnt)+'.txt', 'w', encoding='utf-8')
                    f.write(str({"cot":sample_output_string,"code":code_ini}))
                    f.close()
                    continue

                input3,output3,pre_analyse,code_next = get_wrong_reason(0,path,now_problem_info,problem_id_now,input_format_requirement,explanation11,explanation22,max_x)
                sample_output_string += "\n\n"
                sample_output_string += copy.deepcopy(one_example_cot_format).format(input=str(input3),
                                                                                        output=str(output3),
                                                                                        work_reason=pre_analyse['work_reason'],
                                                                                        error_reason=pre_analyse['wrong_reason'],
                                                                                        revise_code=code_next)


                for idx in range(1,max_x+1):
                    result = subprocess.run(['python3', './problems/' + problem_id_now + '/' + 'judge.py','--code_path','code'+str(idx)+'.py'], capture_output=True,text=True)
                    time.sleep(3)
                    if idx == max_x or result.returncode == 1:
                        code_now = ""
                        with open(path + '/code' + str(idx) + '.py', 'r', encoding='utf-8') as file:
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
