from threading import Thread
from 맞춤법검사 import Spelling
from pandas import DataFrame,merge,read_csv

base_file=read_csv("../Data/사용할리뷰기초데이터.csv",index_col=0)
total_comment=base_file["place_review"]

num=len(total_comment)//5
thread_pool=[]
main_pool=[]
splited_list=[]
for i in range(6):
    main_pool.append(Spelling(name=f"{i}번째_객체",headless=True))
    splited_list.append(total_comment.iloc[num*i:num*(i+1)])

for i in range(6):
    sub_thread=Thread(target=main_pool[i].transform,args=(splited_list[i],))
    thread_pool.append(sub_thread)
    sub_thread.start()

for thread in thread_pool:
    thread.join()

for pool in main_pool:
    try:
        pool.driver.quit()
    except:
        print("이미 완료되었습니다")

total=sum([pool.sentence_list for pool in main_pool],[])
df=read_csv("../KoBERT/사용할리뷰기초데이터.csv",index_col=0)

transform_=DataFrame(total,columns=["멎춤법검사완"])
transform_

수정본=merge(df.reset_index().drop(columns=["index"])
      ,transform_,left_index=True,right_index=True)
