
from selenium.webdriver import Chrome
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import visibility_of_all_elements_located
from selenium.webdriver.chrome.options import Options
from pandas import DataFrame,read_excel,read_csv
from collections.abc import Iterable 
from tqdm import tqdm

class Spelling:
    def __init__(self,name,headless=True) -> None:
        '''
        셀레니움 실행시 기본 옵션값을 설정해야합니다.
        또한 내려받는 파일의 형식을 변경할 수 있습니다.
        '''
        self.name=name
        self.chrome_options=Options()
        if headless:
            self.chrome_options.add_argument('--headless')  # 헤드리스 모드 설정
            self.chrome_options.add_argument('--no-sandbox')
            self.chrome_options.add_argument('--disable-dev-shm-usage')
        
        self.driver=Chrome(options=self.chrome_options) if headless else Chrome()

        path="https://m.search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query=%EB%84%A4%EC%9D%B4%EB%B2%84+%EB%A7%9E%EC%B6%A4%EB%B2%95"

        self.driver.get(path)
        pass

    def sentence_trunaction(self,sentence:str,base_length:int=300):
        if len(sentence) <= base_length:
            return [sentence]
        else:
            splited_list=sentence.split(".")
            check_length=lambda x:len(x)<=base_length
            if all(map(check_length,splited_list)):
                return splited_list
            else:
                waring_message=Warning(f"문장의 길이가 {base_length}보다 깁니다.확인해보세요")
                return [sentence]
            
    def read_file(self,file_path:str="../KoBERT/사용할리뷰기초데이터.csv",feature_col="place_review",label_col="감성"):
        use_data=read_csv(file_path,index_col=0)
        comment_array,label_array=use_data[feature_col],use_data[label_col]

        # result=[]
        # for comment in comment_array:
        # global sentence_trunaction
        #     result.append(self.sentence_trunaction(comment))

        return comment_array,label_array

    def spelling_check(self,sentence):
        self.검사창=WebDriverWait(self.driver,3).until(
            visibility_of_all_elements_located((By.CSS_SELECTOR,"textarea")))[0]
        
        self.검사창.send_keys(sentence)

        self.검사하기 = WebDriverWait(self.driver,3).until(
            visibility_of_all_elements_located((By.CSS_SELECTOR,".inspection_bx button")))[0]
        self.검사하기.click()

        검사기다리기=WebDriverWait(self.driver,10).until(
            lambda driver:driver.find_element(By.CSS_SELECTOR,".result_bx > .result_text").text!='맞춤법 검사 중입니다. 잠시만 기다려주세요.')
        
        검사결과=WebDriverWait(self.driver,3).until(
            visibility_of_all_elements_located((By.CSS_SELECTOR,".result_bx > .result_text")))[0].text
        
        self.검사창.clear()
        return 검사결과

    def transform(self,sentence_list=None,label_list=None):
        if sentence_list is None:
            self.sentence_list,self.label_list=self.read_file()
        else:
            self.sentence_list=sentence_list
            self.label_list=label_list
            pass
        '''
        직접 추가할 경우 바로 아래의 함수 적용
        '''
        if isinstance(self.sentence_list,str):
            #단일 문장이 들어갔을 때
            checked_sentence=self.sentence_trunaction(self.sentence_list)

        elif isinstance(self.sentence_list,Iterable):
            #여러개의 문장을 받았을 때
            checked_sentence=list(map(self.sentence_trunaction,self.sentence_list))
        else:
            self.driver.quit()
            raise(TypeError("잘못된 형식입니다"))
        
        transform_result=[]
        for sentence in tqdm(checked_sentence):
            if isinstance(sentence,str):
                sub_result=self.spelling_check(sentence)
            else:
                sub_result="".join(map(self.spelling_check,sentence))
            transform_result.append(sub_result)
        if len(self.sentence_list)==len(transform_result):
            #추출하기 위해 장치해둠
            self.sentence_list=transform_result
            self.driver.quit()
        else:
            self.driver.quit()
            raise Warning("개수가 맞지않습니다")
        return transform_result
    
    def to_file(self,file_path,format="csv"):
        
        df=DataFrame([self.sentence_list,self.label_list],columns=["feature","label"])
        if format=="excel":
            df.to_excel(file_path)
        else:
            df.to_csv(file_path)
