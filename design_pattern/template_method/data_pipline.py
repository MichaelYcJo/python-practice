
'''
특정 작업을 처리하는 파이프라인을 구축하는 시나리오
데이터를 읽고, 처리하고, 결과를 저장하는 일련의 작업을 수행하는 데이터 파이프라인을 구축한다고 가정해 봅시다. 이 파이프라인은 다음과 같은 단계를 포함합니다:

데이터를 읽는다.
데이터를 전처리한다.
데이터를 분석한다.
분석 결과를 저장한다.

'''

from abc import ABC, abstractmethod

class DataPipeline(ABC):
    '''
    데이터 파이프라인의 각 단계를 정의하는 추상 클래스. 
    이 클래스는 execute() 메소드를 통해 전체 파이프라인을 실행하는 논리를 캡슐화. 
    각 단계는 추상 메소드로 선언되어 서브클래스에서 구현
    '''
    def execute(self):
        data = self.read_data()
        processed_data = self.preprocess_data(data)
        results = self.analyze_data(processed_data)
        self.save_results(results)

    @abstractmethod
    def read_data(self):
        pass

    @abstractmethod
    def preprocess_data(self, data):
        pass

    @abstractmethod
    def analyze_data(self, processed_data):
        pass

    @abstractmethod
    def save_results(self, results):
        pass


class CSVDataPipeline(DataPipeline):
    '''
    DataPipeline을 상속받아 CSV 파일에서 데이터를 읽고, 전처리하고, 분석한 후, 
    결과를 JSON 파일로 저장하는 파이프라인을 구현
    '''
    def read_data(self):
        print("Reading data from CSV file")
        # CSV 파일을 읽는 로직
        return "raw_csv_data"

    def preprocess_data(self, data):
        print("Preprocessing CSV data")
        # CSV 데이터를 전처리하는 로직
        return "processed_csv_data"

    def analyze_data(self, processed_data):
        print("Analyzing CSV data")
        # 데이터를 분석하는 로직
        return "csv_analysis_results"

    def save_results(self, results):
        print("Saving results to JSON file")
        # 분석 결과를 JSON 파일로 저장하는 로직
        pass

class DatabasePipeline(DataPipeline):
    '''
    DataPipeline을 상속받아 데이터베이스에서 데이터를 읽고, 전처리하고, 분석한 후, 
    결과를 데이터베이스 테이블에 저장하는 파이프라인을 구현
    '''
    def read_data(self):
        print("Reading data from database")
        # 데이터베이스에서 데이터를 읽는 로직
        return "raw_db_data"

    def preprocess_data(self, data):
        print("Preprocessing database data")
        # 데이터베이스 데이터를 전처리하는 로직
        return "processed_db_data"

    def analyze_data(self, processed_data):
        print("Analyzing database data")
        # 데이터를 분석하는 로직
        return "db_analysis_results"

    def save_results(self, results):
        print("Saving results to database table")
        # 분석 결과를 데이터베이스 테이블로 저장하는 로직
        pass

# 사용 예시
csv_pipeline = CSVDataPipeline()
csv_pipeline.execute()

print()

db_pipeline = DatabasePipeline()
db_pipeline.execute()


'''
Reading data from CSV file
Preprocessing CSV data
Analyzing CSV data
Saving results to JSON file

Reading data from database
Preprocessing database data
Analyzing database data
Saving results to database table


'''