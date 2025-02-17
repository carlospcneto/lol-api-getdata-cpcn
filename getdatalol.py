import logging, requests, os, yaml, shutil, time, datetime, requests, traceback
import pandas as pd
from collections import namedtuple
import argparse

# Dados Teste
# puuid = "smVq8PGKNLFVatly_fkSFLP_WLYlKULVsPGepMCWWqGMg3oq1ktg5fnporX3aKmiiFlZEApJEwY59w"
# gameName = "iResi"
# tagLine = "BR1"
# game = "lor" ou "val"
# encryptedPUUID = "smVq8PGKNLFVatly_fkSFLP_WLYlKULVsPGepMCWWqGMg3oq1ktg5fnporX3aKmiiFlZEApJEwY59w"
# championId = 67,
# count = 3
# page = 1

POSSIBLE_REGIONS = ["AMERICAS", "ASIA", "EUROPE", "SEA"]
POSSIBLE_SERVERS = ["BR1", "EUN1", "EUW1", "JP1", "KR", "LA1", "LA2", "NA1", "OC1", "PH2", "RU", "SG2", "TH2", "TR1", "TW2", "VN2"]
POSSIBLE_QUEUES = ["RANKED_SOLO_5x5", "RANKED_FLEX_SR", "RANKED_FLEX_TT"]
POSSIBLE_URLS = [
    # 2024-10-03
    # ACCOUNT-V1
    "https://{region}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}?api_key={api_key}",
    "https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}?api_key={api_key}",
    "https://{region}.api.riotgames.com/riot/account/v1/active-shards/by-game/{game}/by-puuid/{puuid}?api_key={api_key}",
    # "/riot/account/v1/accounts/me", # Cannot execute. This API endpoint is not available in your policy    
    # CHAMPION-MASTERY-V4
    "https://{server}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{encryptedPUUID}?api_key={api_key}",
    "https://{server}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{encryptedPUUID}/by-champion/{championId}?api_key={api_key}",
    "https://{server}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{encryptedPUUID}/top?count={count}&api_key={api_key}",
    "https://{server}.api.riotgames.com/lol/champion-mastery/v4/scores/by-puuid/{encryptedPUUID}?api_key={api_key}",
    # CHAMPION-V3
    "https://{server}.api.riotgames.com/lol/platform/v3/champion-rotations?api_key={api_key}",
    # LEAGUE-EXP-V4
    "https://{server}.api.riotgames.com}/lol/league-exp/v4/entries/{queue}/{tier}/{division}?page={page}&api_key={api_key}",   
    # LEAGUE-V4
    "https://{server}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/{queue}?api_key={api_key}",
    "https://{server}.api.riotgames.com/lol/league/v4/entries/by-summoner/{encryptedSummonerId}?api_key={api_key}",
    "https://{server}.api.riotgames.com/lol/league/v4/entries/{queue}/{tier}/{division}?page={page}&api_key={api_key}",
    "https://{server}.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/{queue}?api_key={api_key}",
    "https://{server}.api.riotgames.com/lol/league/v4/leagues/{leagueId}?api_key={api_key}",
    "https://{server}.api.riotgames.com/lol/league/v4/masterleagues/by-queue/{queue}?api_key={api_key}"
    # LOL-CHALLENGES-V1
    "https://{server}.api.riotgames.com/lol/challenges/v1/challenges/config?api_key={api_key}",
    "https://{server}.api.riotgames.com/lol/challenges/v1/challenges/percentiles?api_key={api_key}",
    "https://{server}.api.riotgames.com/lol/challenges/v1/challenges/{challengeId}/config?api_key={api_key}",
    "https://{server}.api.riotgames.com/lol/challenges/v1/challenges/{challengeId}/leaderboards/by-level/{level}?limit={limit}&api_key={api_key}",
    "https://{server}.api.riotgames.com/lol/challenges/v1/challenges/{challengeId}/percentiles?api_key={api_key}",
    "https://{server}.api.riotgames.com/lol/challenges/v1/player-data/{puuid}",
    # LOL-RSO-MATCH-V1
    # "/lol/rso-match/v1/matches/ids", # Cannot execute. This API endpoint is not available in your policy
    # "https://{region}.api.riotgames.com/lol/rso-match/v1/matches/{matchId}", # Cannot execute. This API endpoint is not available in your policy 
    # "https://{region}.api.riotgames.com/lol/rso-match/v1/matches/{matchId}/timeline", # Cannot execute. This API endpoint is not available in your policy
    # MATCH-V5
    "https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids{queryParams}&api_key={api_key}", 
    # startTime timestamp , endTime timestamp, queue int = 420, type string  = ranked, start = 0, count = 100
    "https://{region}.api.riotgames.com/lol/match/v5/matches/{matchId}?api_key={api_key}",
    "https://{region}.api.riotgames.com/lol/match/v5/matches/{matchId}/timeline?api_key={api_key}",
    # SPECTATOR-V5
    "https://{server}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{encryptedSummonerId}?api_key={api_key}",
    "https://{server}.api.riotgames.com/lol/spectator/v5/featured-games?api_key={api_key}",
    # SUMMONER-V4
    "https://{server}.api.riotgames.com/fulfillment/v1/summoners/by-puuid/{rsoPUUID}?api_key={api_key}",
    "https://{server}.api.riotgames.com/lol/summoner/v4/summoners/by-account/{encryptedAccountId}?api_key={api_key}",
    "https://{server}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}?api_key={api_key}",
    "https://{server}.api.riotgames.com/lol/summoner/v4/summoners/me?api_key={api_key}?api_key={api_key}",
    "https://{server}.api.riotgames.com/lol/summoner/v4/summoners/{encryptedSummonerId}?api_key={api_key}"
]

class Logger():
    """
    Singleton class to log messages to a file.    
    """    

    _instance = None

    @staticmethod
    def get_instance():
        if Logger._instance is None:
            Logger._instance = Logger()
        return Logger._instance

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Create a file handler and set the file path
        if not os.path.exists('logs'):
            os.makedirs('logs')
        self.log_file = 'logs/mainlog.log'
        self.file_handler = logging.FileHandler(self.log_file)

        # Create a formatter and set the format for log messages
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(self.formatter)

        # Add the file handler to the logger
        self.logger.addHandler(self.file_handler)

    # Add the logging methods to the Logger class
    def debug(self, msg):
        self.logger.debug(msg)
        print(msg)

    def info(self, msg):
        self.logger.info(msg)
        print(msg)

    def warning(self, msg):
        self.logger.warning(msg)
        print(msg)

    def error(self, msg):
        self.logger.error(msg)
        print(msg)

    def critical(self, msg):
        self.logger.critical(msg)
        print(msg)

def save_parquet(df: pd.DataFrame, path: str, partition_cols: list[str], mode='append'):
    """
    Save a DataFrame to a parquet file.
    Args:
    - df (pd.DataFrame): the DataFrame to be saved.
    - path (str): the path to save the DataFrame.
    - partition_cols (list[str]): the columns to be used as partitions.
    - mode (str): the mode to save the DataFrame. It can be 'append' or 'overwrite'.
    """
    # Implementado somente para 1 particao e 1 coluna de particao
    try:
        if mode == "overwrite":
            part_path = f"{path}/{partition_cols[0]}={df[partition_cols[0]].unique()[0]}"
            if os.path.exists(part_path):
                shutil.rmtree(part_path)

        if os.path.exists(path):
            df_old = pd.read_parquet(path)
            df = pd.concat([df_old, df])
                
            
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)

        df.to_parquet(path, partition_cols=partition_cols)
    except Exception as e:
        raise e

def verifica_api_key(api_key: str) -> bool:
    """
    Verify if the api key is valid

    Args:
        api_key (str): _description_

    Returns:
        bool: result for the verification
    """
    try:
        response = requests.get(f"https://br1.api.riotgames.com/lol/status/v4/platform-data?api_key={api_key}")
        if response.status_code == 200:
            return True
        elif response.status_code == 403:
            return False
    except:
        return False

def get_last_partition(partition_col: str, df: pd.DataFrame = None, path_parquet: str = "") -> str:
    """
    Get the last partition of a DataFrame.
    Args:
    - partition_col (str): the partition column.
    - df (pd.DataFrame): the DataFrame to get the last partition from.
    - path_parquet (str): the path to the parquet file to get the last partition from.
    Returns:
    - str: the last partition.
    """
    if path_parquet != "":
        if os.path.exists(path_parquet):
            df = pd.read_parquet(path_parquet)
        else:
            return None

    last_partition = df[partition_col].cat.as_ordered().max()

    return last_partition

class GetDataLol:
    """
    Class to retrieve data from the League of Legends API.
    """

    def __init__(self, api_key: str, server: str = "BR1", region: str = "AMERICAS", output_path: str = ""):

        self._logger = Logger.get_instance()
        self._logger.info(f"Iniciando GetDataLol, para o servidor: {server} e região: {region}.")
        
        if region not in POSSIBLE_REGIONS:
            self._logger.error(f"Região inválida: {region}.")
            raise ValueError(f"Região inválida: {region}.")
        self._region = region
        
        if server not in POSSIBLE_SERVERS:
            self._logger.error(f"Região inválida: {server}.")
            raise ValueError(f"Região inválida: {server}.")                
        self._server = server
        
        self._api_key = api_key
        self._count_request = 0
        
        if output_path == "":            
            self._path_data = os.path.dirname(os.path.abspath(__file__))
        else:
            self._path_data = output_path
            
        if not os.path.exists(self._path_data):
            os.makedirs(self._path_data)

    def get_data(self, url: str, **kwargs):

        if not url in POSSIBLE_URLS:
            self._logger.error(f"Endpoint inválido: {url}.")
            raise ValueError(f"Endpoint inválido: {url}.")
        
        try:
            url_mounted = url.format(server=self._server, region=self._region, api_key=self._api_key, **kwargs)
        except Exception as e:
            self._logger.error(f"Erro ao montar a URL: {e}")
            raise e
        
        self._logger.info(f"Requisititando dados de: {url_mounted}")

        try:                        
            self._count_request += 1
            continua = True
            while continua:                
                response = requests.get(url_mounted)            
                if response.status_code == 200: 
                    self._logger.info("Dados requisitados com sucesso")
                    continua = False                    
                else:
                    self._logger.error(f"Erro ao requisitar dados: {response.status_code}")
                    time.sleep(1)
                
        except requests.RequestException as e:
            self._logger.error(f"Erro na requisição: {e}")    
        except Exception as e:
            self._logger.error(f"Error: {e}")

        return response.json()     

    def challenger_daily(self, dat_ref_carga: str) -> list[str]:
        
        self._logger.info(f"Obtendo dados da liga challenger, dia {dat_ref_carga}")
        name_table = "tb_challenger_daily"
                        
        if get_last_partition("dat_ref_carga", path_parquet=f"{self._path_data}/{name_table}.parquet") == dat_ref_carga:
            self._logger.info("Os dados da liga challenger já foram carregados hoje.")
            df = pd.read_parquet(f"{self._path_data}/{name_table}.parquet")
            df = df[df['dat_ref_carga'] == dat_ref_carga]
            return df['summonerId'].tolist()
        else:
            try:
                end_point = "https://{server}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/{queue}?api_key={api_key}" 
                r1 = self.get_data(end_point, queue="RANKED_SOLO_5x5")
                df = pd.DataFrame(r1['entries'])
                df = df.sort_values(by='leaguePoints', ascending=False)
                df['position'] = range(1, len(df) + 1)
                df = df.reset_index(drop=True)
                df['dat_ref_carga'] = dat_ref_carga
                
                ### Formatando a tabela ###
                df['summonerId'] = df['summonerId'].astype(str)
                df['leaguePoints'] = df['leaguePoints'].astype(int)
                df['rank'] = df['rank'].astype(str)
                df['wins'] = df['wins'].astype(int)
                df['losses'] = df['losses'].astype(int)
                df['veteran'] = df['veteran'].astype(bool)
                df['inactive'] = df['inactive'].astype(bool)
                df['freshBlood'] = df['freshBlood'].astype(bool)
                df['hotStreak'] = df['hotStreak'].astype(bool)
                df['position'] = df['position'].astype(int)
                df['dat_ref_carga'] = df['dat_ref_carga'].astype(str)
                
                save_parquet(df, f'{self._path_data}/{name_table}.parquet', partition_cols=['dat_ref_carga'], mode='overwrite')
                return df['summonerId'].tolist()
            except Exception as e:
                self._logger.error(f"Erro ao obter os dados da liga challenger: {e}")
                return []            

    def summoners(self, summoners: list[str], dat_ref_carga: str):

        try:        
            name_table = "tb_summoners"
            name_table_hist = f"{name_table}_hist"
            end_point = "https://{server}.api.riotgames.com/lol/summoner/v4/summoners/{encryptedSummonerId}?api_key={api_key}"

            if os.path.exists(f"{self._path_data}/{name_table}.parquet"):
                df = pd.read_parquet(f"{self._path_data}/{name_table}.parquet")
            else:
                df = pd.DataFrame(columns=['id', 'accountId', 'puuid', 'profileIconId', 'revisionDate', 'summonerLevel', 'last_dat_ref_carga'])
                df['id'] = df['id'].astype(str)
                df['accountId'] = df['accountId'].astype(str)
                df['puuid'] = df['puuid'].astype(str)
                df['profileIconId'] = df['profileIconId'].astype(int)
                df['revisionDate'] = df['revisionDate'].astype(int)
                df['summonerLevel'] = df['summonerLevel'].astype(int)
                df['last_dat_ref_carga'] = df['last_dat_ref_carga'].astype(str)

            df_hist = pd.DataFrame(columns=['id', 'alter_data', 'dat_ref_carga'])
            df_hist['id'] = df_hist['id'].astype(str)
            df_hist['alter_data'] = df_hist['alter_data'].astype(object)
            df_hist['dat_ref_carga'] = df_hist['dat_ref_carga'].astype(str)

            df_aux = pd.DataFrame(columns=df.columns)
            
            for sum in summoners:
                # Pega os dados da API
                r = self.get_data(end_point, encryptedSummonerId=sum)

                # Verificar se ja tem o summoner no df
                id_row = df[(df['id'] == r['id'])]

                # Tenho ja info do summoner no df, vou verificar se todas as colunas estao iguais 
                list_cols = list(df.columns)
                list_cols.remove('id')
                list_cols.remove('last_dat_ref_carga')

                if not id_row.empty:
                    dif = {}
                    for col in list_cols:                        
                        # Verifico as diferenças
                        if id_row[(id_row[col] == r[col])].empty:                            
                            dif[col] = r[col]

                    # Houve alteração de alguma coluna
                    if len(dif) > 0:
                        # Remove the row with matching id
                        # df = df[df['id'] != r['id']]
                        # apaga a linha da tabela
                        part_path = f"{self._path_data}/{name_table}.parquet/id={r['id']}"
                        if os.path.exists(part_path):
                            shutil.rmtree(part_path)

                        r["last_dat_ref_carga"] = dat_ref_carga

                        df_r = pd.DataFrame([r])
                        # Append the updated summoner data to the dataframe                        
                        df_aux = pd.concat([df_aux, df_r], ignore_index=True)

                        hist = pd.DataFrame([{"id" : r["id"], "alter_data" : dif, "dat_ref_carga" : dat_ref_carga}])

                        df_hist = pd.concat([df_hist, hist], ignore_index=True)
                else:
                    # Nao tenho info do summoner no df, entao adiciono a info da data de atualizacao                    
                    r['last_dat_ref_carga'] = dat_ref_carga
                    # Uno meu df auxiliar com o novo summoner
                    df_aux = pd.concat([df_aux, pd.DataFrame([r])], ignore_index=True)

                    filtered_dict = {key: value for key, value in r.items() if key in list_cols}

                    hist = pd.DataFrame([{"id" : r["id"], "alter_data" : filtered_dict ,"dat_ref_carga" : dat_ref_carga}])

                    df_hist = pd.concat([df_hist, hist], ignore_index=True)
            
        
            if len(df_aux) > 0:                
                save_parquet(df_aux, f'{self._path_data}/{name_table}.parquet', partition_cols=["id"] , mode='overwrite')
            
            if len(df_hist) > 0:
                save_parquet(df_hist, f'{self._path_data}/{name_table_hist}.parquet', partition_cols=["id"] , mode='append')
                    
        except Exception as e:
            self._logger.error(f"Erro ao obter os dados dos summoners: {e}")
            self._logger.error(traceback.format_exc())  # Captura e registra o traceback completo
            
            return False    

    def matchs_today(self, summoners: list[str], dat_ref_carga: str):

        def processa_match(match_data: dict) -> pd.DataFrame:
            # Converte a parte de metadata e informacoes dos pariticpantes em dataframe
            df_metadata = pd.DataFrame(match_data['metadata'])
            df_info_participants = pd.DataFrame(match_data['info']['participants'])
            # Uner os dois a partir do puuid
            merged_df = pd.merge(df_metadata, df_info_participants, left_on='participants', right_on='puuid')

            # Copia a parte de info e remove a informacao de participantes que ja usamos                    
            info_game = match_data['info'].copy()
            info_game.pop('participants')

            # Pega as informacoes dos times
            info_teams = info_game['teams']
            info = info_game.copy()
            info.pop('teams')

            # Gera o matcId na parte de info
            info['matchId'] = f"{info['platformId']}_{info['gameId']}"
            df_info = pd.DataFrame([info])
            df_info_teams = pd.DataFrame(info_teams)
            df_info_teams.drop('win', axis=1, inplace=True)

            # Une todos os dataframes
            final_df = pd.merge(merged_df, df_info_teams, on='teamId')
            final_df = pd.merge(final_df, df_info, on='matchId')

            return final_df

        def processa_timeline(matchId: str, match_timeline: dict) -> pd.DataFrame:
            match_timeline_frames = match_timeline['info']['frames']
            matrix = []
            for index, value in enumerate(match_timeline_frames):
                row = {}
                row['matchId'] = matchId
                row['event'] = index
                
                for event in value['events']:
                    row_aux = row.copy()
                    for key in event.keys():            
                        row_aux[key] = event[key]
                    matrix.append(row_aux)

                row['timestamp'] = value['timestamp']

                for p_f in value['participantFrames'].keys():
                    
                    row_aux = row.copy()

                    for key in value['participantFrames'][p_f].keys():
                        row_aux[key] = value['participantFrames'][p_f][key]
                    matrix.append(row_aux)
            return pd.DataFrame(matrix)
        
        try:
            # Converter a lista de summonersid para puuid

            df_sum = pd.read_parquet(f"{self._path_data}/tb_summoners.parquet")

            puuids = df_sum[df_sum['id'].isin(summoners)]['puuid'].tolist()

            if len(puuids) != len(summoners):
                self._logger.error(f"Dados faltantes em summoners table para algum invocador: {e}")
                return False
            
            dat_ref_carga_datetime = datetime.datetime.strptime(dat_ref_carga, "%Y-%m-%d")
            # Set start time to today at 00:00:00
            start_time = datetime.datetime(dat_ref_carga_datetime.year, dat_ref_carga_datetime.month, dat_ref_carga_datetime.day, 0, 0, 0)
            start_timestamp = int(time.mktime(start_time.timetuple()))

            # Set end time to today at 23:59:59
            end_time = datetime.datetime(dat_ref_carga_datetime.year, dat_ref_carga_datetime.month, dat_ref_carga_datetime.day, 23, 59, 59)
            end_timestamp = int(time.mktime(end_time.timetuple()))

            queue = 420

            matchs_today = []
            for puuid in puuids:                                            
                queryParams = f"?startTime={start_timestamp}&endTime={end_timestamp}&queue={queue}"
                r = self.get_data("https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids{queryParams}&api_key={api_key}", puuid=puuid, queryParams=queryParams)                
                matchs_today.extend(r)

            self._logger.info(f"Matchs encontrados: {len(matchs_today)}")
            
            df_match_info_saved = None
            if os.path.exists(f"{self._path_data}/tb_matchs_infos.parquet"):
                df_match_info_saved = pd.read_parquet(f"{self._path_data}/tb_matchs_infos.parquet")
                
            df_match_time_saved = None
            if os.path.exists(f"{self._path_data}/tb_matchs_timeline.parquet"):            
                df_match_time_saved = pd.read_parquet(f"{self._path_data}/tb_matchs_timeline.parquet")
            
            df_matchs_infos = None
            df_matchs_timeline = None
            for matchid in matchs_today:
                
                if df_match_info_saved is not None:
                    if matchid in df_match_info_saved['matchId'].values:
                        self._logger.info(f"Match {matchid} já existe no dataframe salvo.")
                        continue
                    
                # Get the match data
                match_data = self.get_data("https://{region}.api.riotgames.com/lol/match/v5/matches/{matchId}?api_key={api_key}", matchId=matchid)

                df_match_data = processa_match(match_data)

                if df_matchs_infos is None:
                    df_matchs_infos = df_match_data
                else:
                    df_matchs_infos = pd.concat([df_matchs_infos, df_match_data], ignore_index=True)
                
                if df_match_time_saved is not None:
                    if matchid in df_match_time_saved['matchId'].values:
                        self._logger.info(f"Match {matchid} já existe no dataframe salvo.")
                        continue

                # Get the match timeline
                match_timeline = self.get_data("https://{region}.api.riotgames.com/lol/match/v5/matches/{matchId}/timeline?api_key={api_key}", matchId=matchid)

                df_match_timeline = processa_timeline(matchid, match_timeline)

                if df_matchs_timeline is None:
                    df_matchs_timeline = df_match_timeline
                else:
                    df_matchs_timeline = pd.concat([df_matchs_timeline, df_match_data], ignore_index=True)

                                
            save_parquet(df_matchs_infos, f'{self._path_data}/tb_matchs_infos.parquet', partition_cols=["matchId"], mode='overwrite')     
            save_parquet(df_matchs_timeline, f'{self._path_data}/tb_matchs_timeline.parquet', partition_cols=["matchId"], mode='overwrite')

            return True
        except Exception as e:
            self._logger.error(f"Erro ao obter os dados dos matchs: {e}")
            return False


def main(api_key: str,
         output_path: str,
         method: str):
    """
    Principal function to get the data from the API
    
    method: str, the method to extract data. It can be 'all'
    
        'all'
            O padrão, 
            
    """       
    
    if not verifica_api_key(api_key):
        logger.error("API KEY inválida.")
    else:
        logger.info("API KEY validada.")
        objget = GetDataLol(api_key, server="BR1", region="AMERICAS", output_path=output_path)
        dat_ref_carga = datetime.date.today().strftime("%Y-%m-%d")
    
        if method == "all":
            # Challenger Daily - Informação do Top 200 do Challenger da Região
            top_200_summoners = objget.challenger_daily(dat_ref_carga) # objget_br
            # Salva as informaçoẽs dos summoners
            objget.summoners(top_200_summoners, dat_ref_carga) # objget_br
            objget.matchs_today(top_200_summoners, dat_ref_carga) # objget_americas
            
        logger.info("Dados extraídos com sucesso.")
    
    

if __name__ == "__main__":
    logger = Logger.get_instance()
    logger.info("----- Iniciando a execução. -----")
    path_here = os.path.dirname(os.path.abspath(__file__))
    try:        
        parser = argparse.ArgumentParser()
        parser.add_argument("--api_key", type=str, help="API key from Riot Developer Portal.", required=True)
        parser.add_argument("--output_path", type=str, default=path_here, help="Path to save the outputs parquets.")
        parser.add_argument("--method", type=str, default="all", help="Method to extract data.")
        args = parser.parse_args()
        logger.info("Pegando os dados do argparse.")
    except:
        try:
            with open(f"{path_here}/parameters.yaml", "r") as file:
                parameters = yaml.safe_load(file)
            Parameters = namedtuple("Parameters", parameters.keys())
            args = Parameters(*parameters.values())
            logger.info("Pegando os dados do parameters.yaml.")
        except:
            raise Exception("Error to load parameters.")
    
    main(api_key= args.api_key, output_path=args.output_path, method=args.method)
    logger.info("----- Finalizando a execução. -----")

