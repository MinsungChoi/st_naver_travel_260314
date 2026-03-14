# Streamlit Cloud 배포 필수 파일 안내

Streamlit Cloud(GitHub 연동) 배포를 위해 반드시 필요한 파일들과 업로드 시 주의사항을 정리해 드립니다.

## 1. 필수 파일 리스트 (GitHub에 올릴 것)

GitHub 저장소(Repository)의 루트에 아래 파일들이 위치해야 합니다.

- **`src/app.py`**: 대시보드 메인 소스 코드
- **`src/naver_api.py`**: 네이버 API 연동 모듈
- **`requirements.txt`**: 배포 환경에서 설치할 라이브러리 목록
- **`.gitignore`**: GitHub에 절대 올리면 안 되는 파일들(예: `.env`, `.venv`)을 지정하는 파일

---

## 2. 제외 파일 (절대 올리지 마세요! ⚠️)

- **`.env`**: 개인 API 키가 들어있으므로 보안상 보안이 필요합니다.
- **`.venv`**: 가상환경 폴더는 배포 환경에서 자동으로 생성되므로 올릴 필요가 없습니다.

---

## 3. Streamlit Cloud 설정(Secrets) 방법

`.env` 파일 대신 Streamlit Cloud 대시보드에서 API 키를 설정해야 합니다.

1. Streamlit Cloud 앱 설정(Settings) 메뉴로 이동합니다.
2. **Secrets** 탭을 클릭합니다.
3. 아래 내용을 복사해서 붙여넣고 저장(Save)하세요:

```toml
NAVER_CLIENT_ID = "사용자의_클라이언트_아이디"
NAVER_CLIENT_SECRET = "사용자의_클라이언트_시크릿"
```

위와 같이 설정하면 코드 내의 `os.getenv()`가 이 Secret 값을 읽어오게 됩니다.
