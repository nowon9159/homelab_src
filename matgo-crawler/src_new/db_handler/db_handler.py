import json
import pymongo
import mysql.connector

class DBHandler:
    def __init__(self, mongo_config=None, mysql_config=None):
        """
        DB Handler 초기화
        
        :param mongo_config: MongoDB 연결 설정 딕셔너리
        :param mysql_config: MySQL 연결 설정 딕셔너리
        """
        # MongoDB 연결
        if mongo_config:
            self.mongo_client = pymongo.MongoClient(mongo_config['host'], mongo_config['port'])
            self.mongo_db = self.mongo_client[mongo_config['database']]
        
        # MySQL 연결
        if mysql_config:
            self.mysql_connection = mysql.connector.connect(**mysql_config)
            self.mysql_cursor = self.mysql_connection.cursor()

    def _convert_value_to_str(self, value):
        """
        다양한 타입의 값을 문자열로 변환하는 보조 메서드
        
        :param value: 변환할 값
        :return: 변환된 문자열
        """
        if isinstance(value, list):
            # 리스트를 쉼표로 구분된 문자열로 변환
            return ', '.join(map(str, value))
        elif isinstance(value, dict):
            # 딕셔너리를 JSON 문자열로 변환
            return json.dumps(value)
        elif value is None:
            return ''
        else:
            # 기타 타입은 문자열로 변환
            return str(value)

    def insert_to_mongodb(self, collection_name, json_data):
        """
        MongoDB에 JSON 데이터 삽입
        
        :param collection_name: 컬렉션 이름
        :param json_data: 삽입할 JSON 데이터
        """
        mongo_collection = self.mongo_db[collection_name]
        
        if isinstance(json_data, dict):
            mongo_collection.insert_one(json_data)
        elif isinstance(json_data, list):
            mongo_collection.insert_many(json_data)
        else:
            raise ValueError("Invalid JSON data type for MongoDB")

    def insert_to_mysql(self, table_name, json_data):
        """
        MySQL에 JSON 데이터 삽입
        
        :param table_name: 테이블 이름
        :param json_data: 삽입할 JSON 데이터
        """
        def process_mysql_data(data):
            """
            JSON 데이터를 MySQL에 맞게 전처리
            """
            # 값들을 문자열로 변환
            processed_data = {
                k: self._convert_value_to_str(v) for k, v in data.items()
            }
            return processed_data

        if isinstance(json_data, dict):
            # 단일 레코드 처리
            processed_data = process_mysql_data(json_data)
            columns = ', '.join(processed_data.keys())
            values = tuple(processed_data.values())
            
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({', '.join(['%s']*len(values))})"
            self.mysql_cursor.execute(query, values)
            self.mysql_connection.commit()
        
        elif isinstance(json_data, list):
            if not json_data:
                return
            
            # 다중 레코드 처리
            processed_data = [process_mysql_data(item) for item in json_data]
            
            # 첫 번째 레코드의 키를 기준으로 columns 결정
            columns = ', '.join(processed_data[0].keys())
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({', '.join(['%s']*len(processed_data[0]))})"
            
            # 다중 행 삽입
            values_list = [tuple(item.values()) for item in processed_data]
            self.mysql_cursor.executemany(query, values_list)
            self.mysql_connection.commit()
        else:
            raise ValueError("Invalid JSON data type for MySQL")

    def close_connections(self):
        """
        데이터베이스 연결 종료
        """
        if hasattr(self, 'mongo_client'):
            self.mongo_client.close()
        
        if hasattr(self, 'mysql_connection'):
            self.mysql_cursor.close()
            self.mysql_connection.close()

# 사용 예시
def example_usage():
    # 설정 예시
    mongo_config = {
        'host': 'localhost',
        'port': 27017,
        'database': 'mydb'
    }

    mysql_config = {
        'host': 'localhost',
        'user': 'username',
        'password': 'password',
        'database': 'mydb'
    }

    # DBHandler 인스턴스 생성
    db_handler = DBHandler(mongo_config, mysql_config)

    # 복잡한 JSON 데이터 예시
    complex_data = {
        'name': 'John Doe',
        'age': 30,
        'juice': ['apple', 'pear'],
        'tags': ['developer', 'engineer'],
        'address': {
            'city': 'New York',
            'zip': '10001'
        }
    }

    # MySQL에 데이터 삽입
    db_handler.insert_to_mysql('users', complex_data)

    # 연결 종료
    db_handler.close_connections()