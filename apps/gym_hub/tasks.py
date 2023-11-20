import pandas as pd
import numpy as np
import io
from django.http import HttpResponse
import logging
import pytz
indian_tz = pytz.timezone('Asia/Kolkata')
from apps.gym_hub.models import (MasterRate, UploadDueBook, DataUploadTask,
                                   CollectionUpdate,TempTableBB,TempTableCollectionUpdate,
                                   ChannelPartner, ErrorTable,
                                   UploadBlueBook, TempTable)
from amibe.celery import app
from datetime import datetime
logger = logging.getLogger(__name__)
# this is for saving the commission slab data into the DB


@app.task(queue='high_priority')
def save_commision_slab_rate_task(df):
    print("Received the commission slab task in celery")
    # model_obj=[MasterRate(**row) for row in df.to_dict(orient='records')]
    model_obj = [MasterRate(**row) for row in df]
    MasterRate.objects.bulk_create(model_obj)
    logging.info("the data has been saved in commission slab table")
    return "Data has been saved to Data Upload task and Commission Slab"

# #this is for saving the Due Book data into the DB
@app.task(queue="high_priority")
def save_blue_due_book_task(latest_data_upload_id):
    logging.info("Received the BB DB task in celery")
    comm_sl_df = MasterRate.objects.filter(is_active=True).values()
    comm_sl_df = pd.DataFrame(comm_sl_df)
    # comm_sl_df['rate']=comm_sl_df['rate'].fillna(0,inplace=True)
    try:
        temp_df=TempTable.objects.all().values()
        temp_df = pd.DataFrame(temp_df)
    except Exception as  e:
        print(f"the exception found for temp table-{e}")
    try:
        bb_temp_df=TempTableBB.objects.all().values()
        bb_temp_df = pd.DataFrame(bb_temp_df) 
    except Exception as  e:
        print(f"the exception found for bb temp table-{e}")
    try:
        channel_partner_df = ChannelPartner.objects.all().values()
        channel_partner_df = pd.DataFrame(channel_partner_df)
    except Exception as  e:
        print(f"the exception found for channel partner table-{e}")
    lenh = temp_df.shape[0]
    lenh1 = bb_temp_df.shape[0]
    comm_len=comm_sl_df.shape[0]
    count = 0
    bbcount=0    
    data_upload_obj = DataUploadTask.objects.filter(id=latest_data_upload_id)
    if comm_sl_df.shape[0] == 0 and channel_partner_df.shape[0] == 0:
        task_end_time = datetime.now()
        data_upload_obj.update(ended_at=task_end_time)
        data_upload_obj.update(status="Data not available either in Commission Slab and Channel Partners")
        print("Data not available either in Commission Slab and Channel Partners")
        TempTable.objects.all().delete()
        TempTableBB.objects.all().delete()
        return "Data has not been saved due to no records in channel partner or commission slab"
    elif channel_partner_df.shape[0] == 0:
        task_end_time = datetime.now()
        data_upload_obj.update(ended_at=task_end_time)
        data_upload_obj.update(status="Data not available in  Channel Partners")
        print("Data not available in  Channel Partners")
        TempTable.objects.all().delete()
        TempTableBB.objects.all().delete()
        return "Data has not been saved due to no records in channel partner or commission slab"
    elif comm_sl_df.shape[0] == 0:
        task_end_time = datetime.now()
        data_upload_obj.update(ended_at=task_end_time)
        data_upload_obj.update(status="Data not available in  commission slab")
        print("Data not available in  commission slab")
        TempTable.objects.all().delete()
        TempTableBB.objects.all().delete()
        return "Data has not been saved due to no records in channel partner or commission slab"
    else:
        channel_partner_df=channel_partner_df.rename(columns={"channel_code": "bank_channel_partner", "plan_code": "product_code"})
        channel_partner_df=channel_partner_df.rename(columns={"plan_code": "product_code"})
        if 'rule_name' in temp_df.columns:
            temp_df.drop(columns=['rule_name'], inplace=True)
        if 'rule_name' in bb_temp_df.columns:
            bb_temp_df.drop(columns=['rule_name'], inplace=True)
        if 'filename' in temp_df.columns:
            temp_df.drop(columns=['filename'], inplace=True)
        if 'filename' in bb_temp_df.columns:
            bb_temp_df.drop(columns=['filename'], inplace=True)
        if temp_df.shape[0] !=0:
            temp_df['is_match_with_channel_partners']="No"
            temp_df = temp_df.merge(channel_partner_df, how="left",
                                on=["bank_channel_partner","product_code"])
            temp_df.drop(columns=["id_x","id_y", "concatenate"], inplace=True) 
            temp_df.drop(columns=['is_active'], inplace=True)           
            temp_df.loc[temp_df['rule_name'].notna(),'is_match_with_channel_partners']=str("Yes")
            temp_df['rule_name'].fillna('', inplace=True)
            if temp_df.shape[0] !=0:     
                temp_df['policy_term'] = pd.to_numeric(temp_df['policy_term'], errors='coerce')
                temp_df['premium_paying_term'] = pd.to_numeric(temp_df['premium_paying_term'], errors='coerce')
                temp_df['modal_based_premium'] = temp_df['modal_based_premium'].astype(float)
                comm_sl_df['rate'] = comm_sl_df['rate'].astype(float)
                conditions = (
                    (temp_df['product_code'].isin(comm_sl_df['product_code'])) &
                    (comm_sl_df['year_from'].le(temp_df['year_banding']) & (temp_df['year_banding'].le(comm_sl_df['year_to']))) &
                    (comm_sl_df['pt_from'].le(temp_df['policy_term']) & (temp_df['policy_term'].le(comm_sl_df['pt_to']))) &
                    (comm_sl_df['ppt_from'].le(temp_df['premium_paying_term']) & (temp_df['premium_paying_term'].le(comm_sl_df['ppt_to']))) &
                    (comm_sl_df['premium_from'].le(temp_df['modal_based_premium']) & (temp_df['modal_based_premium'].le(comm_sl_df['premium_to']))) &
                    (comm_sl_df['ape_from'].le(temp_df['annualized_target_premium']) & (temp_df['annualized_target_premium'].le(comm_sl_df['ape_to']))) &
                    (comm_sl_df['rule_name'].eq(temp_df['rule_name'])) &
                    (comm_sl_df['is_staff'].eq(temp_df['staff_non_staff']))
                )
                print("11"*100,temp_df['product_code'].shape[0])
                print("22"*100,temp_df['modal_based_premium'].shape[0])
                print("33"*100,temp_df['commision_amount'].shape[0])
                print("44"*100,conditions.shape)
                if lenh <= comm_len:
                    # Ensure both sides have the same length
                    selected_values = temp_df['modal_based_premium'] * comm_sl_df['rate'] / 100
                    temp_df.loc[conditions, 'commision_amount'] = selected_values[conditions]

                    # temp_df.loc[conditions, 'commision_amount'] = temp_df['modal_based_premium'] * comm_sl_df['rate'] / 100
                else:
                    temp_df['commision_amount'] = np.where(conditions,
                                                    temp_df['modal_based_premium'] * comm_sl_df['rate'] / 100,
                                                    temp_df['commision_amount'])
                    count = np.sum(conditions)
                    data_upload_obj.update(
                        status=f"Out of {lenh} records {count} has been processed for Due Book.")
                df = pd.DataFrame(temp_df)
                task_end_time = datetime.now()
                df['created_on']=task_end_time
                # df.drop(columns=['is_active'],inplace=True)
                print(f"the total record from due table {df.shape[0]}")
                if data_upload_obj.values('action').first()['action']=="UPLOAD":
                    model_obj = [UploadDueBook(**row) for row in df.to_dict(orient='records')]
                    UploadDueBook.objects.bulk_create(model_obj,batch_size=100000)
                if data_upload_obj.values('action').first()['action']=="APPEND":
                    model_obj = [UploadDueBook(**row) for row in df.to_dict(orient='records')]
                    UploadDueBook.objects.bulk_create(model_obj,batch_size=100000)
                if data_upload_obj.values('action').first()['action']=="REPLACE":
                    financial_year=data_upload_obj.values('financial_year').first()['financial_year']
                    UploadDueBook.objects.filter(financial_year=financial_year).delete()
                    model_obj = [UploadDueBook(**row) for row in df.to_dict(orient='records')]
                    UploadDueBook.objects.bulk_create(model_obj,batch_size=100000)
                TempTable.objects.all().delete()                
                data_upload_obj.update(ended_at=task_end_time)
                logging.info("Data have been saved to due book processed")

            else:
                task_end_time = datetime.now()
                data_upload_obj.update(ended_at=task_end_time)
                data_upload_obj.update(
                        status="Data didn't match with channel partners")
                TempTable.objects.all().delete()
                logging.info("Data have not been saved to due book due to no records after merging")

        if bb_temp_df.shape[0]!=0:
            bb_temp_df['is_match_with_channel_partners']="No"
            # bb_temp_df['is_match_with_commission_slab']="No"
            bb_temp_df = bb_temp_df.merge(channel_partner_df, how="left",
                                on=["bank_channel_partner","product_code"])
            bb_temp_df.drop(columns=["id_x","id_y", "concatenate"], inplace=True)
            bb_temp_df.drop(columns=['is_active'], inplace=True)  
            bb_temp_df.loc[bb_temp_df['rule_name'].notna(),'is_match_with_channel_partners']=str("Yes")
            bb_temp_df['rule_name'].fillna('', inplace=True)
            if bb_temp_df.shape[0] != 0:
                bb_temp_df['policy_term'] = pd.to_numeric(bb_temp_df['policy_term'], errors='coerce')
                bb_temp_df['premium_paying_term'] = pd.to_numeric(bb_temp_df['premium_paying_term'], errors='coerce')
                bb_temp_df['modal_based_premium'] = bb_temp_df['modal_based_premium'].astype(float)
                comm_sl_df['rate'] = comm_sl_df['rate'].astype(float)
                conditions = (
                    (bb_temp_df['product_code'].isin(comm_sl_df['product_code'])) &
                    (comm_sl_df['year_from'].le(bb_temp_df['year_banding']) & (bb_temp_df['year_banding'].le(comm_sl_df['year_to']))) &
                    (comm_sl_df['pt_from'].le(bb_temp_df['policy_term']) & (bb_temp_df['policy_term'].le(comm_sl_df['pt_to']))) &
                    (comm_sl_df['ppt_from'].le(bb_temp_df['premium_paying_term']) & (bb_temp_df['premium_paying_term'].le(comm_sl_df['ppt_to']))) &
                    (comm_sl_df['premium_from'].le(bb_temp_df['modal_based_premium']) & (bb_temp_df['modal_based_premium'].le(comm_sl_df['premium_to']))) &
                    (comm_sl_df['ape_from'].le(bb_temp_df['annualized_target_premium']) & (bb_temp_df['annualized_target_premium'].le(comm_sl_df['ape_to']))) &
                    (comm_sl_df['rule_name'].eq(bb_temp_df['rule_name'])) &
                    (comm_sl_df['is_staff'].eq(bb_temp_df['staff_non_staff']))
                )
                if lenh1<=comm_len:
                    selected_values = bb_temp_df['modal_based_premium'] * comm_sl_df['rate'] / 100
                    bb_temp_df.loc[conditions, 'commision_amount'] = selected_values[conditions]
                    # bb_temp_df.loc[conditions, 'commision_amount'] = bb_temp_df['modal_based_premium'] * comm_sl_df['rate'] / 100
                else:
                    bb_temp_df['commision_amount'] = np.where(conditions,
                                                    bb_temp_df['modal_based_premium'] * comm_sl_df['rate'] / 100,
                                                    bb_temp_df['commision_amount'])
                    bbcount = np.sum(conditions)
                    data_upload_obj.update(
                        status=f"Processing Blue Book...")
                    
                data_upload_obj.update(
                        status="Completed...")
                df1 = pd.DataFrame(bb_temp_df)
                task_end_time = datetime.now()
                df1['created_on']=task_end_time                
                # df1.drop(columns=['is_active'],inplace=True)
                if data_upload_obj.values('action').first()['action']=="UPLOAD":
                    model_obj = [UploadBlueBook(**row) for row in df1.to_dict(orient='records')]
                    UploadBlueBook.objects.bulk_create(model_obj,batch_size=100000)
                if data_upload_obj.values('action').first()['action']=="APPEND":
                    model_obj = [UploadBlueBook(**row) for row in df1.to_dict(orient='records')]
                    UploadBlueBook.objects.bulk_create(model_obj,batch_size=100000)
                if data_upload_obj.values('action').first()['action']=="REPLACE":
                    financial_year=data_upload_obj.values('financial_year').first()['financial_year']
                    UploadBlueBook.objects.filter(financial_year=financial_year).delete()
                    model_obj = [UploadBlueBook(**row) for row in df1.to_dict(orient='records')]
                    UploadBlueBook.objects.bulk_create(model_obj,batch_size=100000)            
                TempTableBB.objects.all().delete()    
                data_upload_obj.update(ended_at=task_end_time)
                logging.info("Data have been saved to blue book processed")
            else:
                task_end_time = datetime.now()
                data_upload_obj.update(ended_at=task_end_time)
                data_upload_obj.update(
                        status="Data didn't match with channel partners with blue book")
                TempTableBB.objects.all().delete()
                logging.info("Data have not been saved to blue book due to no records after merging")
        else:
            task_end_time = datetime.now()
            data_upload_obj.update(ended_at=task_end_time)
            data_upload_obj.update(status="Data did not match with Channel Partners BB")
            TempTable.objects.all().delete()
            TempTableBB.objects.all().delete()
            print("Data did not match with Channel Partners and DB or BB")
            return "Data have not been saved to blue book and due book"
            
        
@app.task(queue="high_priority")
def save_error_table(df):
    logging.info("into the errot table----")
    logging.info("0----", type(df))
    # logging.info("--------",df)
    # model_obj=[UploadDueBook(**row) for row in df.to_dict(orient='records')]
    model_obj = [ErrorTable(**row) for row in df]
    ErrorTable.objects.bulk_create(model_obj)
    logging.info("the data has been saved in error table")
    return "Data has been saved to Data Upload task and error table"

@app.task(queue="high_priority")
def update_collection_flag(latest_data_upload_id):
    bb_obj=pd.DataFrame(UploadBlueBook.objects.values('id','collection_flag','actual_due_date','policy_no').filter(financial_year='2023-2024',collection_flag="N"))
    db_obj=pd.DataFrame(UploadDueBook.objects.values('id','collection_flag','actual_due_date','policy_no').filter(financial_year='2023-2024',collection_flag="N"))
    coll_flag_obj=pd.DataFrame(CollectionUpdate.objects.all().values())
    db_obj=pd.DataFrame(db_obj)
    bb_obj=pd.DataFrame(bb_obj)
    coll_flag_obj=pd.DataFrame(coll_flag_obj)
    coll_flag_obj.drop(columns=['id','collection_flag'],inplace=True)
    coll_flag_obj.policy_no=coll_flag_obj.policy_no.astype('str')      
    data_upload_obj = DataUploadTask.objects.filter(id=latest_data_upload_id)[0]
    if db_obj.shape[0] !=0:
        error_df=None
        try:
            error_file = data_upload_obj.error_file.path
            valid=data_upload_obj.valid_records
            invalid=data_upload_obj.error_records
            error_df=pd.read_excel(error_file)
            print("777"*100,error_df.columns)
        except Exception as e:
            print(f"The error in fetching the error file of collection upload- {e}")
        db_obj['policy_no']=pd.to_numeric(db_obj['policy_no'])
        coll_flag_obj['policy_no']=pd.to_numeric(coll_flag_obj['policy_no'])
        print("444444"*100,coll_flag_obj)
        db_merged=db_obj.merge(coll_flag_obj,on=['policy_no'],how="left",indicator=True)
        print("111"*100,db_merged)
        rigth_only=db_obj.merge(coll_flag_obj,on=['policy_no'],how="right",indicator=True)
        print("333"*100,rigth_only)
        rigth_only=rigth_only[rigth_only['_merge']=="right_only"]
        # rigth_only = coll_flag_obj[~(coll_flag_obj['policy_no'].isin(db_merged['policy_no']).fillna("test"))]
        # if error_df.shape[0]!=0:
        if rigth_only.shape[0]!=0:
            rigth_only.drop(columns=['id','actual_due_date','_merge'],inplace=True)
            rigth_only['error_messages']="The policy numbers does not exists"
            if error_df is not None:
                error_df = [df for df in [error_df, rigth_only] if df is not None]
                error_df=pd.concat(error_df,axis=0,ignore_index=True)
            else:
                error_df=rigth_only
        print("000"*100,rigth_only,error_df)
        db_merged.dropna(inplace=True)
        print("999999"*100,db_merged.columns)
        if db_merged.shape[0]!=0:            
            db_merged['actual_due_date']=pd.to_datetime(db_merged['actual_due_date'],format="%Y-%m-%d")
            db_merged=db_merged.sort_values(by=['policy_no','counter','actual_due_date'])
            db_merged['number_of_policy']=db_merged['policy_no'].map(dict(db_merged['policy_no'].value_counts()))
            error_db_df=db_merged[db_merged['number_of_policy']<db_merged['counter']]    
            error_db_df['error_messages']="The row has greater counter value than number of policies."    
            error_db_df.drop_duplicates(subset=['policy_no'],inplace=True) 
            count=error_db_df.shape[0]  
            if error_db_df.shape[0]!=0:
                error_db_df.drop(columns=['number_of_policy','actual_due_date','id'],inplace=True)                
                if error_df is not None:
                    error_df = [df for df in [error_df, error_db_df] if df is not None]
                    error_df=pd.concat(error_df,axis=0,ignore_index=True)
                else:
                    error_df=error_db_df                
                # task_end_time = datetime.now()
                # data_upload_obj.ended_at=task_end_time
                # data_upload_obj.status="The counter are more than number of policies of a particular row, please download the error file for reference."
                # data_upload_obj.valid_records=valid-count
                # data_upload_obj.error_records=invalid+count               
                # data_upload_obj.save()
                logging.info("Data have been saved to due book")
            db_merged=db_merged[db_merged['number_of_policy']>=db_merged['counter']]
            print("db merged--"*100,db_merged)
            visited_policy=[]
            for index,row in db_merged.iterrows():
                counter_value= int(row['counter'])
                if row['policy_no'] not in visited_policy:
                    db_merged.loc[db_merged.index[index:index+counter_value], 'collection_flag'] = 'Y'
                    visited_policy.append(row['policy_no'])
            print("db merged-- second"*100,db_merged)
            for _,row in db_merged.iterrows():
                db_id=row['id']
                db_obj_model=UploadDueBook.objects.filter(id=db_id)
                db_obj_model.update(collection_flag=row['collection_flag'])
            count=error_df.shape[0]
            task_end_time = datetime.now()
            data_upload_obj.ended_at=task_end_time
            data_upload_obj.valid_records=data_upload_obj.total_records-count
            data_upload_obj.error_records=count
            data_upload_obj.status="Uploaded..."
            excel_file=io.BytesIO()
            print("jjj"*100,error_df)
            if error_df is not None:
                with pd.ExcelWriter(excel_file,engine="xlsxwriter", mode="xlsx") as writer:
                    error_df.to_excel(writer,index=False)
            excel_file.seek(0)
            if error_df is not None:
                data_upload_obj.error_file.save('collection_flag_error.xlsx', excel_file)
            data_upload_obj.save()
            logging.info("Data have been saved to due book")
        else:
            task_end_time = datetime.now()
            data_upload_obj.ended_at=task_end_time
            data_upload_obj.status="Data didn't match with Due book or Blue book"
            excel_file=io.BytesIO()
            if error_df is not None:
                with pd.ExcelWriter(excel_file,engine="xlsxwriter", mode="xlsx") as writer:
                    error_df.to_excel(writer,index=False)
            excel_file.seek(0)
            if error_df is not None:
                data_upload_obj.error_file.save('collection_flag_error.xlsx', excel_file)
            data_upload_obj.save()
            logging.info("Data have not been saved to due book due to no records after merging")

    if bb_obj.shape[0]!=0:
        error_df=None
        try:
            error_file = data_upload_obj.error_file.path
            valid=data_upload_obj.valid_records
            invalid=data_upload_obj.error_records
            error_df=pd.read_excel(error_file)
        except Exception as e:
            print(f"The error in fetching the error file of collection upload- {e}")
        bb_obj['policy_no']=pd.to_numeric(bb_obj['policy_no'])
        coll_flag_obj['policy_no']=pd.to_numeric(coll_flag_obj['policy_no'])
        bb_merged=pd.merge(bb_obj,coll_flag_obj,on="policy_no",how="left",indicator=True)
        print("111"*100,bb_merged)
        # bbrigth_only=coll_flag_obj[~coll_flag_obj['policy_no'].isin(bb_merged['policy_no'])]
        # if error_df.shape[0]!=0:
        #     error_df.drop(columns=['id','collection_flag','_merge'],inplace=True)
        #     bbrigth_only=bb_obj.merge(error_df,on=['policy_no'],how="right",indicator=True)
        # else:
        bbrigth_only=bb_obj.merge(coll_flag_obj,on=['policy_no'],how="right",indicator=True)
        bbrigth_only=bbrigth_only[bbrigth_only['_merge']=="right_only"]
        if bbrigth_only.shape[0]!=0:
            bbrigth_only.drop(columns=['id','actual_due_date','_merge'],inplace=True)
            bbrigth_only['error_messages']="The policy numbers does not exists"
            if error_df is not None:
                error_df = [df for df in [error_df, bbrigth_only] if df is not None]
                error_df=pd.concat(error_df,axis=0,ignore_index=True)
            else:
                error_df=bbrigth_only
        error_df.drop_duplicates(inplace=True)
        print("000"*100,bbrigth_only,error_df)
        bb_merged.dropna(inplace=True)
        print("999999"*100,bb_merged.columns)
        if bb_merged.shape[0] !=0:            
            bb_merged['actual_due_date']=pd.to_datetime(bb_merged['actual_due_date'],format="%Y-%m-%d")
            bb_merged=bb_merged.sort_values(by=['policy_no','counter','actual_due_date'])
            bb_merged['number_of_policy']=bb_merged['policy_no'].map(dict(bb_merged['policy_no'].value_counts()))
            error_bb_df=bb_merged[bb_merged['number_of_policy']<bb_merged['counter']]
            error_bb_df['error_messages']="The row has greater counter value than number of policies."
            error_bb_df.drop_duplicates(subset=['policy_no'],inplace=True)
            # count=error_bb_df.shape[0]
            if error_bb_df.shape[0]!=0:
                error_bb_df.drop(columns=['number_of_policy','actual_due_date','id'],inplace=True)
                if error_df is not None:
                    error_df = [df for df in [error_df, error_bb_df] if df is not None]
                    error_df=pd.concat(error_df,axis=0,ignore_index=True)    
                else:
                    error_df=error_bb_df         
                # task_end_time = datetime.now()
                # data_upload_obj.ended_at=task_end_time
                # data_upload_obj.status="The counter are more than number of policies of a particular row, please download the error file for reference."
                # data_upload_obj.save()
                logging.info("Data have not been saved to due book")
                # CollectionUpdate.objects.all().delete()
                # return "data has more counter than no of policies"
            bb_merged=bb_merged[bb_merged['number_of_policy']>=bb_merged['counter']]
            print("bb merged--"*100,bb_merged)
            visited_policy=[]
            for index,row in bb_merged.iterrows():
                counter_value= int(row['counter'])
                if row['policy_no'] not in visited_policy:
                    bb_merged.loc[bb_merged.index[index:index+counter_value], 'collection_flag'] = 'Y'
                    visited_policy.append(row['policy_no'])
                    print("the list",visited_policy)
            print("the bb merged second",bb_merged)
            for _,row in bb_merged.iterrows():
                bb_id=row['id']
                bb_obj_model=UploadBlueBook.objects.filter(id=bb_id)
                bb_obj_model.update(collection_flag=row['collection_flag'])
            error_df.drop_duplicates(inplace=True)
            count=error_df.shape[0]
            print("3333"*100,count)
            task_end_time = datetime.now()
            data_upload_obj.ended_at=task_end_time
            data_upload_obj.valid_records=data_upload_obj.total_records-count
            data_upload_obj.error_records=count
            data_upload_obj.status="Uploaded..."
            excel_file=io.BytesIO()            
            print("6666"*100,error_df)
            if error_df is not None:
                with pd.ExcelWriter(excel_file,engine="xlsxwriter", mode="xlsx") as writer:
                    error_df.to_excel(writer,index=False)
            excel_file.seek(0)
            if error_df is not None:
            # data_upload_obj.update(error_file=excel_file)
                data_upload_obj.error_file.save('collection_flag_error.xlsx', excel_file)
            data_upload_obj.save()
            logging.info("Data have been saved to blue book")
            CollectionUpdate.objects.all().delete()
        else:
            task_end_time = datetime.now()
            data_upload_obj.ended_at=task_end_time
            data_upload_obj.status="Data didn't match with Due book or Blue book"
            excel_file=io.BytesIO()
            if error_df is not None:
                with pd.ExcelWriter(excel_file,engine="xlsxwriter", mode="xlsx") as writer:
                    error_df.to_excel(writer,index=False)
            excel_file.seek(0)
            if error_df is not None:
                data_upload_obj.error_file.save('collection_flag_error.xlsx', excel_file)
            data_upload_obj.save()
            logging.info("Data have not been saved to blue book due to no records after merging")
        CollectionUpdate.objects.all().delete()
    else:
        task_end_time = datetime.now()
        data_upload_obj.ended_at=task_end_time
        data_upload_obj.status="No Records found of Blue or Due Book."  
        data_upload_obj.save()      
        CollectionUpdate.objects.all().delete()
        logging.info("Data have not been saved to due book due to no records after merging")
        
           

@app.task(queue="high_priority")
def download_view_data(filter_params):
    
    logging.info("sample has done"*100)

                # for row_ind in range(0, temp_df.shape[0], 1):
                #     for row_index in range(0, comm_sl_df.shape[0], 1):
                #         if  temp_df['product_code'].iloc[row_ind] == comm_sl_df['product_code'].iloc[row_index] and \
                #             (comm_sl_df['year_from'].iloc[row_index] <= (temp_df['year_banding'].iloc[row_ind]) <= comm_sl_df['year_to'].iloc[row_index]) and \
                #             (comm_sl_df['pt_from'].iloc[row_index] <= int(temp_df['policy_term'].iloc[row_ind]) <= comm_sl_df['pt_to'].iloc[row_index]) and \
                #             (comm_sl_df['ppt_from'].iloc[row_index] <= int(temp_df['premium_paying_term'].iloc[row_ind]) <= comm_sl_df['ppt_to'].iloc[row_index]) and \
                #             (comm_sl_df['premium_from'].iloc[row_index] <= (temp_df['modal_based_premium'].iloc[row_ind]) <= comm_sl_df['premium_to'].iloc[row_index]) and \
                #             (comm_sl_df['ape_from'].iloc[row_index] <= temp_df['annualized_target_premium'].iloc[row_ind] <= comm_sl_df['ape_to'].iloc[row_index]) and \
                #                 (comm_sl_df['rule_name'].iloc[row_index] == temp_df['rule_name'].iloc[row_ind]) and \
                #                 (comm_sl_df['is_staff'].iloc[row_index] == temp_df['staff_non_staff'].iloc[row_ind]):
                            
                #             (temp_df["commision_amount"].iloc[row_ind])=float((temp_df['modal_based_premium'].iloc[row_ind] * comm_sl_df['rate'].iloc[row_index]) / 100)
                #     count += 1