import sys
import http.server
import socketserver
import threading
import json
import time
import iksm
from datetime import datetime


class MyHTTPHandler(http.server.SimpleHTTPRequestHandler):
    # ログ出力を無効化
    def log_message(self, format, *args):
        return


class Stats:
    def __init__(self, dict):
        self.clear_num = dict["clear_num"]
        self.dead_total = dict["dead_total"]
        self.end_time = dict["end_time"]
        self.failure_counts = dict["failure_counts"]
        self.grade_point = dict["grade_point"]
        self.help_total = dict["help_total"]
        self.job_num = dict["job_num"]
        self.kuma_point_total = dict["kuma_point_total"]
        self.my_golden_ikura_total = dict["my_golden_ikura_total"]
        self.my_ikura_total = dict["my_ikura_total"]
        self.start_time = dict["start_time"]
        self.team_golden_ikura_total = dict["team_golden_ikura_total"]
        self.team_ikura_total = dict["team_ikura_total"]


class User:
    def __init__(self, dict = None):
        self.nsaid = dict["nsaid"]
        self.nickname = dict["nickname"]
        self.iksm_session = dict["iksm_session"]
        self.session_token = dict["session_token"]
        self.clear = dict["clear"]
        self.failure = dict["failure"]
        self.grade_point = dict["grade_point"]
        self.failure_counts = dict["failure_counts"]
        self.dead_total = dict["dead_total"]
        self.help_total = dict["help_total"]
        self.team_golden_ikura_total = dict["team_golden_ikura_total"]
        self.team_ikura_total = dict["team_ikura_total"]
        self.my_ikura_total = dict["my_ikura_total"]
        self.my_golden_ikura_total = dict["my_golden_ikura_total"]
        self.kuma_point_total = dict["kuma_point_total"]
        self.job_num = dict["job_num"]


    def reset(self):
        self.clear = 0
        self.failure = 0
        self.help_total = 0
        self.dead_total = 0
        self.failure_counts = [0, 0, 0]
        self.grade_point = 400
        self.my_golden_ikura_total = 0
        self.my_ikura_total = 0
        self.team_golden_ikura_total = 0
        self.team_ikura_total = 0
        self.job_num = 0
        self.kuma_point_total = 0

    def set(self, stats: Stats):
        self.clear = stats.clear_num
        self.failure = stats.job_num - stats.clear_num
        self.help_total = stats.help_total
        self.dead_total = stats.dead_total
        self.failure_counts = stats.failure_counts
        self.grade_point = stats.grade_point
        self.my_golden_ikura_total = stats.my_golden_ikura_total
        self.my_ikura_total = stats.my_ikura_total
        self.team_golden_ikura_total = stats.team_golden_ikura_total
        self.team_ikura_total = stats.team_ikura_total
        self.job_num = stats.job_num
        self.kuma_point_total = stats.kuma_point_total


class SalmonOverlay:
    def __init__(self):
        try:
            with open("config.json", mode="r") as f:
                config = json.load(f)
                self.accounts = list(map(lambda x: User(x), config["account"]))
                self.apitoken = config["apitoken"]
                self.version = config["version"]
        except FileNotFoundError:
            print(f"\r{datetime.now().strftime('%H:%M:%S')} config.jsonがないので作成しました")
            with open("config.json", mode="w") as f:
                content = {
                    "version": None,
                    "apitoken": None,
                    "account": [
                        {
                            "nsaid": None,
                            "iksm_session": None,
                            "session_token": None,
                            "nickname": None,
                            "clear": 0,
                            "failure": 0,
                            "job_num": 0,
                            "help_total": 0,
                            "dead_total": 0,
                            "failure_counts": [0, 0, 0],
                            "grade_point": 0,
                            "my_golden_ikura_total": 0,
                            "my_ikura_total": 0,
                            "team_golden_ikura_total": 0,
                            "team_ikura_total": 0,
                            "kuma_point_total": 0
                        }
                    ]
                }
                json.dump(content, f, indent=4)
            sys.exit()
            

    def update(self, user: User):
        # 共有データを更新
        with open("config.json", mode="w") as f:
            for account in self.accounts:
                if account.session_token == user.session_token:
                    account = user
            json.dump({
                "version": self.version,
                "apitoken": self.apitoken,
                "account": list(map(lambda x: x.__dict__, self.accounts))
            }, f, indent=4, ensure_ascii=False)
        # 表示用のJSONを出力
        with open("stats.json", mode="w") as f:
            json.dump(user.__dict__, f, indent=4, ensure_ascii=False)


def update_forever():
    while True:
        try:
            stats = Stats(iksm._get_coop_summary(user.iksm_session)["summary"]["stats"][0])
            if user.job_num == stats.job_num:
                pass
                # print(f"\r{datetime.now().strftime('%H:%M:%S')} 新しいリザルトが見つかりませんでした")
            else:
                current_time = int(time.time())
                if current_time >= stats.end_time:
                    pass
                    # print(f"\r{datetime.now().strftime('%H:%M:%S')} 新しいリザルトが見つかりませんでした")
                else:
                    user.set(stats)
                    overlay.update(user)
                    print(f"\r{datetime.now().strftime('%H:%M:%S')} 新しいリザルトが見つかり、データを更新しました")
        except KeyboardInterrupt:
            sys.exit(1)
        except (KeyError, ValueError) as e:
            print(e)
        time.sleep(5)


if __name__ == "__main__":
    overlay = SalmonOverlay()
    user: User = None

    print(f"{datetime.now().strftime('%H:%M:%S')} アカウントを選択してください")
    for index, account in enumerate(overlay.accounts):
        print(f"{str(index + 1).ljust(2, ' ')} {str(account.nickname).rjust(10, ' ')}")
    # ユーザのアカウント選択待ち
    while True:
        try:
            index = int(input(""))
            if index <= len(overlay.accounts) and 0 <= index:
                user = overlay.accounts[index - 1]
                break
            else:
                print(f"{datetime.now().strftime('%H:%M:%S')} 有効なアカウント番号を入力してください")
        except KeyboardInterrupt:
            print(f"{datetime.now().strftime('%H:%M:%S')} 終了しました")
            sys.exit(1)
        except ValueError:
            print(f"{datetime.now().strftime('%H:%M:%S')} アカウント番号は整数で入力してください")

    print(f"{datetime.now().strftime('%H:%M:%S')} {user.nickname}が選択されました")
    print(f"{datetime.now().strftime('%H:%M:%S')} {user.nickname}の認証情報が有効かチェックしています")
    if iksm._check_iksm_session_validation(user.iksm_session):
        print(f"{datetime.now().strftime('%H:%M:%S')} {user.nickname}の認証情報は有効でした")
    else:
        print(f"{datetime.now().strftime('%H:%M:%S')} {user.nickname}の認証情報は有効期限切れでした")
        print(f"{datetime.now().strftime('%H:%M:%S')} {user.nickname}の認証情報を再生成します")
        if user.session_token == None:
            print(f"{datetime.now().strftime('%H:%M:%S')} {user.nickname}の有効なセッション情報がありません")
            sys.exit(1)
        else:
            # ユーザのセッショントークンを再生成
            try:
                user.iksm_session = iksm.get_cookie(user.session_token, overlay.version)
                print(f"{datetime.now().strftime('%H:%M:%S')} {user.nickname}の認証情報を更新しました")
                overlay.update(user)
            except Exception as e:
                print(e)
                sys.exit()

    # 最新のバイトリザルトを取得
    stats = Stats(iksm._get_coop_summary(user.iksm_session)["summary"]["stats"][0])
    current_time = int(time.time())
    if current_time >= stats.end_time:
        # 現在時間がバイト終了時間より後なら現在開催中のバイトではないので初期化して上書き
        user.reset()
        overlay.update(user)
        print(f"{datetime.now().strftime('%H:%M:%S')} バイト期間中ではないので初期化しました")
    else:
        user.set(stats)
        overlay.update(user)
        print(f"{datetime.now().strftime('%H:%M:%S')} データを読み込んで上書きしました")

    # 以降、ループする
    thread = threading.Thread(target=update_forever)
    thread.start()

    with socketserver.TCPServer(("", 8080), MyHTTPHandler) as httpd:
        httpd.allow_reuse_address = True
        httpd.serve_forever()
