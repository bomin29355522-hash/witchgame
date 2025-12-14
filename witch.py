from tkinter import *
import random
import time
import pygame

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def img(name):
    return os.path.join(BASE_DIR, "image", name)

def snd(name):
    return os.path.join(BASE_DIR, "sound", name)


# =================(한 곳에서 조절) =================
WIN_W = 750
WIN_H = 600
BG_WIDTH = WIN_W
SPAWN_X = WIN_W + 50

# ================= Enemy 클래스 =================
class Enemy:
    def __init__(self, canvas, img):
        self.canvas = canvas
        self.img = img
        # 화면 오른쪽 바깥에서 생성되도록
        self.me = canvas.create_image(SPAWN_X, random.randint(50, WIN_H-50), image=img)

    def update(self):
        self.canvas.move(self.me, -10, 0)

    def pos(self):
        return self.canvas.coords(self.me)

    def delete(self):
        self.canvas.delete(self.me)

# ================= ShootingGame 클래스=================
class ShootingGame:
    def __init__(self):
        self.win = Tk() #윈도우 생성
        self.win.title("마녀 게임") #제목 설정
        self.win.geometry(f"{WIN_W}x{WIN_H}") #윈도우크기
        self.canvas = Canvas(self.win, width=WIN_W, height=WIN_H)
        self.canvas.pack()

        # ================= 이미지 =================
        
        self.bullet_img = PhotoImage(file=img("bullet.png"))
       
        self.player_left_img = PhotoImage(file=img("witch.left.png"))
        self.player_right_img = PhotoImage(file=img("witch.right.png"))

        self.monster_imgs = [
            PhotoImage(file=img("monster1.png")),
            PhotoImage(file=img("monster2.png")),
            PhotoImage(file=img("monster3.png"))
        ]

        self.bg_imgs = [
            PhotoImage(file=img("background1.png")),
            PhotoImage(file=img("background2.png")),
            PhotoImage(file=img("background3.png"))
        ]

        self.start_bg_img = PhotoImage(file=img("start_background.png"))
        self.ending_img = PhotoImage(file=img("ending_background.png"))


        
        # 배경 두 장 이어붙여 스크롤 
        self.bg1_id = self.canvas.create_image(0,0,image=self.bg_imgs[0], anchor=NW)
        self.bg2_id = self.canvas.create_image(BG_WIDTH,0,image=self.bg_imgs[0], anchor=NW)

        self.player = self.canvas.create_image(100,300,image=self.player_right_img)
        self.direction = "right"

        self.keys = set()
        # 키 이벤트 
        self.win.bind("<KeyPress>", self.onPress)
        self.win.bind("<KeyRelease>", self.onRelease)

        self.last_fire = 0
        self.bullets = []     
        self.enemies = []

        self.score = 0
        self.level = 1
        self.player_life = 3

        #play bgm
        pygame.init()
        pygame.mixer.music.load(snd("Opening.mp3"))
        pygame.mixer.music.play(-1)

        #Effect sound
        self.sounds=pygame.mixer
        self.sounds.init()
        self.s_effect1 = self.sounds.Sound(snd("aw1.mp3"))
       
        self.level_up_text = None
        self.running = True

        # ================= 안내문 =================
        self.key_info = self.canvas.create_text(
            400, 20,
            fill="white",
            font=("Times", 15, "italic bold"),
            text="입력키: ↑, ↓, ←, →, space",
            tags="ui"
        )

        # 시작화면 호출
        self.show_start_screen()

        self.win.mainloop()

    # ================= 키 이벤트 =================
    def onPress(self, e):
        self.keys.add(e.keycode)

    def onRelease(self, e):
        if e.keycode in self.keys:
            self.keys.remove(e.keycode)

    # ================= 총알 생성 =================
    def fire_bullet(self):
        now = time.time()
        if now - self.last_fire > 0.3: 
            self.last_fire = now
            px, py = self.canvas.coords(self.player)

            # 총알 이미지를 방향에 따라 생성
            if self.direction == "right":
                b = self.canvas.create_image(px+30, py, image=self.bullet_img)
                self.bullets.append((b, "right"))
            else:
                b = self.canvas.create_image(px-30, py, image=self.bullet_img)
                self.bullets.append((b, "left"))

    # ================= 몬스터 생성 =================
    def spawn_enemy(self):
        #모든 레벨에서 몬스터 계속 스폰
        if random.randint(0,30)==0:
            img = random.choice(self.monster_imgs)
            self.enemies.append(Enemy(self.canvas,img))

    # ================= 충돌처리 =================
    def check_collision(self):
        # 총알 -> 몬스터 충돌 (한 방에 죽음)
        for b, direction in self.bullets[:]:
            
            coords_b = self.canvas.coords(b)
            if not coords_b:
                continue
            if len(coords_b) == 2:
                bx, by = coords_b
            else:
                bx, by = coords_b[0], coords_b[1]
            for e in self.enemies[:]:
                ex, ey = e.pos()
                if ex is None or ey is None:
                    continue
                if abs(bx-ex) < 30 and abs(by-ey) < 30:
                    # 몬스터 즉시 삭제
                    e.delete()
                    if e in self.enemies:
                        self.enemies.remove(e)

                    try:
                        self.s_effect1.play()
                    except:
                        pass

                    # 점수 증가
                    self.score += 1
                    # 총알 삭제
                    try:
                        self.canvas.delete(b)
                        if (b,direction) in self.bullets:
                            self.bullets.remove((b,direction))
                    except:
                        pass
                    break

        # 플레이어와 몬스터 충돌 -> Life 감소, 몬스터 삭제
        px, py = self.canvas.coords(self.player)
        for e in self.enemies[:]:
            ex, ey = e.pos()
            if ex is None or ey is None:
                continue
            if abs(px-ex) < 30 and abs(py-ey) < 30:
                # 플레이어 라이프 감소
                self.player_life -= 1
                # 충돌한 몬스터 제거
                e.delete()
                if e in self.enemies:
                    self.enemies.remove(e)

    # ================= 레벨/배경  =================
    def update_level(self):
        # 1 -> 2  score >= 10
        if self.score >= 10 and self.level == 1:
            self.level = 2
            self.canvas.itemconfig(self.bg1_id, image=self.bg_imgs[1])
            self.canvas.itemconfig(self.bg2_id, image=self.bg_imgs[1])
            self.show_levelup()

        # 2 -> 3 score >= 20
        elif self.score >= 20 and self.level == 2:
            self.level = 3
            self.canvas.itemconfig(self.bg1_id, image=self.bg_imgs[2])
            self.canvas.itemconfig(self.bg2_id, image=self.bg_imgs[2])
            self.show_levelup()

    #  NEXT LEVEL 메시지
    def show_levelup(self):
        if self.level_up_text:
            self.canvas.delete(self.level_up_text)
        #"NEXT LEVEL!" 표시
        self.level_up_text = self.canvas.create_text(WIN_W//2, WIN_H//2, text=f"NEXT LEVEL!\n(Level {self.level})", font=("Arial",28,"bold"), fill="yellow")
        self.win.after(1000, lambda: self.canvas.delete(self.level_up_text))

    # ================= 배경 =================
    def scroll_bg(self):
        for bg in [self.bg1_id, self.bg2_id]:
            self.canvas.move(bg,-2,0)
        # 재배치
        if self.canvas.coords(self.bg1_id)[0] <= -BG_WIDTH:
            self.canvas.coords(self.bg1_id, BG_WIDTH, 0)
        if self.canvas.coords(self.bg2_id)[0] <= -BG_WIDTH:
            self.canvas.coords(self.bg2_id, BG_WIDTH, 0)

    # ================= Score / Life =================
    def draw_status(self):
        self.canvas.delete("status")
        self.canvas.create_text(80,20,text=f"SCORE: {self.score}",fill="red",font=("Arial",15),tags="status")
        self.canvas.create_text(80,40,text=f"LIFE: {self.player_life}",fill="red",font=("Arial",15),tags="status")

    # ================= 시작화면 함수 =================
    def show_start_screen(self):
        # 배경 이미지 표시
        self.start_bg = self.canvas.create_image(0,0,image=self.start_bg_img,anchor="nw")

        # 게임 제목
        self.title_text = self.canvas.create_text(
            WIN_W//2, 120,
            text="     마녀가 괴물을 죽여서 \n 숲을 깨끗하게 만드는 게임",
            fill="white",
            font=("Times",35,"bold")
        )

        # 게임 설명 / 조작법
        self.desc_text = self.canvas.create_text(
            WIN_W//2, WIN_H//2 - 20,
            text="게임 설명:\n몬스터를 죽이면 점수가 올라갑니다.\n마법으로 괴물을 물리치자!🧙🏻",
            fill="white",
            font=("Arial",16),
            justify="center"
        )

        # 시작 안내 
        self.start_msg = self.canvas.create_text(
            WIN_W//2, WIN_H - 60,
            text="SPACE를 눌러 시작하세요",
            fill="yellow",
            font=("Arial",28,"bold")
        )

        
        self.win.bind("<space>", self.start_game)

    def start_game(self, event=None):
        
        for item in [self.start_bg, getattr(self, "title_text", None), getattr(self, "desc_text", None), getattr(self, "start_msg", None)]:
            try:
                if item is not None:
                    self.canvas.delete(item)
            except:
                pass

        try:
            self.win.unbind("<space>")
        except:
            pass

        # 이제 진짜 게임 
        self.loop()

    # ================= 메인 루프 =================
    def loop(self):

        if not self.running:
            return

        # --- 플레이어 이동 & 이미지 변경 ---
        if 37 in self.keys:  # 왼쪽
            self.canvas.move(self.player,-5,0)
            self.direction="left"
            self.canvas.itemconfig(self.player,image=self.player_left_img)
        elif 39 in self.keys:  # 오른쪽
            self.canvas.move(self.player,5,0)
            self.direction="right"
            self.canvas.itemconfig(self.player,image=self.player_right_img)

        # 수직 이동
        if 38 in self.keys:  # 위
            self.canvas.move(self.player,0,-5)
        elif 40 in self.keys:  # 아래
            self.canvas.move(self.player,0,5)

        # 마지막 방향 유지
        if 37 not in self.keys and 39 not in self.keys:
            if self.direction=="left":
                self.canvas.itemconfig(self.player,image=self.player_left_img)
            else:
                self.canvas.itemconfig(self.player,image=self.player_right_img)

        # 공격
        if 32 in self.keys:
            self.fire_bullet()

        # 총알 이동
        # 총알 이미지 이동
        for b, direction in self.bullets[:]:
            if direction=="right":
                self.canvas.move(b,12,0)
            else:
                self.canvas.move(b,-12,0)

            coords = self.canvas.coords(b)
            if not coords:
               
                try:
                    if (b,direction) in self.bullets:
                        self.bullets.remove((b,direction))
                except:
                    pass
                continue

            bx = coords[0]
            if bx > WIN_W or bx < 0:
                try:
                    self.canvas.delete(b)
                    if (b,direction) in self.bullets:
                        self.bullets.remove((b,direction))
                except:
                    pass

        # 몬스터 생성 
        self.spawn_enemy()

        # 몬스터 이동
        for e in self.enemies:
            e.update()

        # 충돌 
        self.check_collision()

        # 레벨업 (배경 전환 및 NEXT LEVEL 표시)
        self.update_level()

        # 배경 
        self.scroll_bg()

        # 상태 표시
        self.draw_status()

        # 엔딩 체크: 레벨3 상태에서 score >= 30이면 엔딩으로
        if self.level == 3 and self.score >= 30:
            try:
                pygame.mixer.music.stop()
            except:
                pass
            # 엔딩 연출: 이미지 교체 및 텍스트, 루프 종료
            self.running = False
            # 엔딩 배경 
            self.canvas.create_image(0,0,image=self.ending_img,anchor=NW)
            self.canvas.create_text(WIN_W//2,WIN_H//2 - 40,text="GAME CLEAR!",font=("Arial",36,"bold"),fill="red")
            self.canvas.create_text(WIN_W//2,WIN_H//2 + 10,text="마녀는 괴물을 다 해치웠다.",font=("Arial",20),fill="red")
            self.canvas.create_text(WIN_W//2,WIN_H//2 + 50,text="@음 이제 숲이 깨끗하군!@",font=("Arial",18),fill="red")
            return

        # 게임오버 체크
        if self.player_life <= 0:
            try:
                pygame.mixer.music.stop()
            except:
                pass
            self.running = False
            self.canvas.create_text(WIN_W//2,WIN_H//2-30,text="GAME OVER",font=("Arial",40),fill="red")
            self.canvas.create_text(WIN_W//2,WIN_H//2+50,text="   숲은 괴물들로 가득 찼고 \n   마녀는 집을 잃었다..",font=("Arial",30),fill="red")

            return

        self.win.after(33,self.loop)


# ================= 게임 실행 =================
ShootingGame()

