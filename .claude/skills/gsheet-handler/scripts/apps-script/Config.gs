/**
 * Config.gs - API 설정 관리
 */

const CONFIG = {
  RAW_KEYWORD_TAB: 'Raw_키워드',
  RAW_TREND_TAB: 'Raw_트렌드',
  DATALAB_URL: 'https://openapi.naver.com/v1/datalab/search',
  SEARCHAD_URL: 'https://api.searchad.naver.com/keywordstool'
};

function getApiKeys() {
  const props = PropertiesService.getScriptProperties();
  return {
    NAVER_CLIENT_ID: props.getProperty('NAVER_CLIENT_ID') || '',
    NAVER_CLIENT_SECRET: props.getProperty('NAVER_CLIENT_SECRET') || '',
    NAVER_AD_ACCESS_LICENSE: props.getProperty('NAVER_AD_ACCESS_LICENSE') || '',
    NAVER_AD_SECRET_KEY: props.getProperty('NAVER_AD_SECRET_KEY') || '',
    NAVER_AD_CUSTOMER_ID: props.getProperty('NAVER_AD_CUSTOMER_ID') || ''
  };
}

function saveApiSettings(settings) {
  const props = PropertiesService.getScriptProperties();
  for (const [key, value] of Object.entries(settings)) {
    if (value && value.trim() !== '') {
      props.setProperty(key, value.trim());
    }
  }
}

function showSettingsDialog() {
  const keys = getApiKeys();
  const html = HtmlService.createHtmlOutput(`
    <!DOCTYPE html>
    <html>
    <head>
      <base target="_top">
      <style>
        * { box-sizing: border-box; }
        body { font-family: Arial, sans-serif; padding: 20px; margin: 0; }
        h2 { color: #1a73e8; margin-bottom: 20px; font-size: 18px; }
        .section { background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
        .section-title { font-size: 14px; font-weight: bold; margin-bottom: 10px; color: #1a73e8; }
        .form-group { margin-bottom: 12px; }
        label { display: block; margin-bottom: 4px; font-weight: bold; color: #333; font-size: 13px; }
        input[type="text"], input[type="password"] { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 12px; }
        .btn { padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .btn-primary { background: #4285f4; color: white; }
        .btn-secondary { background: #f1f3f4; color: #5f6368; }
        .buttons { display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px; }
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
            .withSuccessHandler(function() { alert('저장 완료'); google.script.host.close(); })
            .withFailureHandler(function(e) { alert('오류: ' + e.message); })
            .saveApiSettings(settings);
        }
      </script>
    </body>
    </html>
  `).setWidth(420).setHeight(480);
  SpreadsheetApp.getUi().showModalDialog(html, 'API 설정');
}

function generateSignature(timestamp, method, uri, secretKey) {
  const message = timestamp + '.' + method + '.' + uri;
  const signature = Utilities.computeHmacSha256Signature(message, secretKey);
  return Utilities.base64Encode(signature);
}
