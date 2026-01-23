/**
 * Config.gs - API 설정 관리
 *
 * 이 파일을 먼저 Apps Script에 추가하세요.
 * 파일 추가: + 버튼 > 스크립트 > 이름: Config
 */

// ========== 전역 설정 ==========
const CONFIG = {
  // 탭 이름
  RAW_KEYWORD_TAB: 'Raw_키워드',
  RAW_TREND_TAB: 'Raw_트렌드',
  DASHBOARD_TAB: '키워드_대시보드',

  // API 엔드포인트
  DATALAB_URL: 'https://openapi.naver.com/v1/datalab/search',
  SEARCHAD_URL: 'https://api.searchad.naver.com/keywordstool'
};

// ========== API 키 가져오기 ==========
function getApiKeys() {
  const props = PropertiesService.getScriptProperties();
  return {
    // 네이버 데이터랩
    NAVER_CLIENT_ID: props.getProperty('NAVER_CLIENT_ID') || '',
    NAVER_CLIENT_SECRET: props.getProperty('NAVER_CLIENT_SECRET') || '',
    // 네이버 검색광고
    NAVER_AD_ACCESS_LICENSE: props.getProperty('NAVER_AD_ACCESS_LICENSE') || '',
    NAVER_AD_SECRET_KEY: props.getProperty('NAVER_AD_SECRET_KEY') || '',
    NAVER_AD_CUSTOMER_ID: props.getProperty('NAVER_AD_CUSTOMER_ID') || ''
  };
}

// ========== API 키 저장 ==========
function saveApiSettings(settings) {
  const props = PropertiesService.getScriptProperties();
  for (const [key, value] of Object.entries(settings)) {
    if (value && value.trim() !== '') {
      props.setProperty(key, value.trim());
    }
  }
}

// ========== API 설정 다이얼로그 ==========
function showSettingsDialog() {
  const keys = getApiKeys();
  const html = HtmlService.createHtmlOutput(`
    <!DOCTYPE html>
    <html>
    <head>
      <base target="_top">
      <style>
        * { box-sizing: border-box; }
        body { font-family: 'Noto Sans KR', Arial, sans-serif; padding: 20px; margin: 0; }
        h2 { color: #1a73e8; margin-bottom: 20px; font-size: 18px; }
        .section { background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
        .section-title { font-size: 14px; font-weight: bold; margin-bottom: 10px; color: #1a73e8; }
        .form-group { margin-bottom: 12px; }
        label { display: block; margin-bottom: 4px; font-weight: bold; color: #333; font-size: 13px; }
        input[type="text"], input[type="password"] {
          width: 100%; padding: 8px; border: 1px solid #ddd;
          border-radius: 4px; font-size: 12px;
        }
        .btn { padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .btn-primary { background: #4285f4; color: white; }
        .btn-primary:hover { background: #3367d6; }
        .btn-secondary { background: #f1f3f4; color: #5f6368; }
        .btn-secondary:hover { background: #e8eaed; }
        .buttons { display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px; }
        .status { padding: 10px; border-radius: 4px; margin-bottom: 15px; font-size: 13px; }
        .status.success { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
      </style>
    </head>
    <body>
      <h2>API 설정</h2>

      <div class="section">
        <div class="section-title">네이버 데이터랩 API</div>
        <div class="form-group">
          <label>Client ID</label>
          <input type="text" id="datalab_id" value="${keys.NAVER_CLIENT_ID}">
        </div>
        <div class="form-group">
          <label>Client Secret</label>
          <input type="password" id="datalab_secret" value="${keys.NAVER_CLIENT_SECRET}">
        </div>
      </div>

      <div class="section">
        <div class="section-title">네이버 검색광고 API</div>
        <div class="form-group">
          <label>Access License</label>
          <input type="text" id="ad_license" value="${keys.NAVER_AD_ACCESS_LICENSE}">
        </div>
        <div class="form-group">
          <label>Secret Key</label>
          <input type="password" id="ad_secret" value="${keys.NAVER_AD_SECRET_KEY}">
        </div>
        <div class="form-group">
          <label>Customer ID</label>
          <input type="text" id="ad_customer" value="${keys.NAVER_AD_CUSTOMER_ID}">
        </div>
      </div>

      <div class="buttons">
        <button class="btn btn-secondary" onclick="google.script.host.close()">취소</button>
        <button class="btn btn-primary" onclick="saveSettings()">저장</button>
      </div>

      <script>
        function saveSettings() {
          const settings = {
            NAVER_CLIENT_ID: document.getElementById('datalab_id').value,
            NAVER_CLIENT_SECRET: document.getElementById('datalab_secret').value,
            NAVER_AD_ACCESS_LICENSE: document.getElementById('ad_license').value,
            NAVER_AD_SECRET_KEY: document.getElementById('ad_secret').value,
            NAVER_AD_CUSTOMER_ID: document.getElementById('ad_customer').value
          };

          google.script.run
            .withSuccessHandler(function() {
              alert('설정이 저장되었습니다.');
              google.script.host.close();
            })
            .withFailureHandler(function(error) {
              alert('오류: ' + error.message);
            })
            .saveApiSettings(settings);
        }
      </script>
    </body>
    </html>
  `)
  .setWidth(420)
  .setHeight(480);

  SpreadsheetApp.getUi().showModalDialog(html, 'API 설정');
}

// ========== HMAC-SHA256 서명 생성 (검색광고 API용) ==========
function generateSignature(timestamp, method, uri, secretKey) {
  const message = timestamp + '.' + method + '.' + uri;
  const signature = Utilities.computeHmacSha256Signature(message, secretKey);
  return Utilities.base64Encode(signature);
}
