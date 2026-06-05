/**
 * VF 출고탭 연결 테스트 스크립트
 * 실행: node test-outbound-connection.js
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const https = require('https');

class OutboundConnectionTester {
  constructor() {
    this.results = {
      envFile: { exists: false, valid: false, content: '' },
      localData: { exists: false, valid: false, itemCount: 0 },
      server: { reachable: false, status: null, responseTime: 0 },
      summary: { passed: 0, failed: 0, total: 3 }
    };
  }

  // 1. .env 파일 확인
  checkEnvFile() {
    const envPath = path.join(process.cwd(), '.env');
    
    try {
      if (fs.existsSync(envPath)) {
        const content = fs.readFileSync(envPath, 'utf8');
        this.results.envFile.exists = true;
        this.results.envFile.content = content;
        
        // OUTBOUND_GOOGLE_SHEET_URL 확인
        const hasSheetUrl = content.includes('OUTBOUND_GOOGLE_SHEET_URL');
        this.results.envFile.valid = hasSheetUrl;
        
        console.log('✅ .env 파일 존재');
        if (hasSheetUrl) {
          console.log('✅ OUTBOUND_GOOGLE_SHEET_URL 설정됨');
        } else {
          console.log('⚠️ OUTBOUND_GOOGLE_SHEET_URL 설정되지 않음');
        }
      } else {
        console.log('❌ .env 파일 없음');
      }
    } catch (error) {
      console.log('❌ .env 파일 확인 실패:', error.message);
    }
  }

  // 2. 로컬 데이터 파일 확인
  checkLocalDataFile() {
    const dataPath = path.join(process.cwd(), 'public', 'outbound-data.json');
    
    try {
      if (fs.existsSync(dataPath)) {
        const content = fs.readFileSync(dataPath, 'utf8');
        this.results.localData.exists = true;
        
        try {
          const data = JSON.parse(content);
          this.results.localData.valid = true;
          this.results.localData.itemCount = data.items?.length || 0;
          
          console.log(`✅ 로컬 데이터 파일 존재 (${this.results.localData.itemCount}개 항목)`);
          console.log(`   마지막 업데이트: ${data.lastUpdated || '없음'}`);
        } catch (parseError) {
          console.log('❌ 로컬 데이터 JSON 파싱 실패:', parseError.message);
        }
      } else {
        console.log('❌ 로컬 데이터 파일 없음: public/outbound-data.json');
      }
    } catch (error) {
      console.log('❌ 로컬 데이터 파일 확인 실패:', error.message);
    }
  }

  // 3. 서버 연결 테스트
  async testServerConnection() {
    const testUrl = 'http://220.121.225.76:5174/outbound';
    const startTime = Date.now();
    
    return new Promise((resolve) => {
      const req = http.get(testUrl, (res) => {
        const responseTime = Date.now() - startTime;
        this.results.server.reachable = true;
        this.results.server.status = res.statusCode;
        this.results.server.responseTime = responseTime;
        
        console.log(`✅ 서버 응답: ${res.statusCode} (${responseTime}ms)`);
        
        let data = '';
        res.on('data', (chunk) => {
          data += chunk;
        });
        
        res.on('end', () => {
          // HTML 응답 확인 (간단히)
          const isHtml = data.includes('<!DOCTYPE html>') || data.includes('<html');
          const hasError = data.includes('OUTBOUND_GOOGLE_SHEET_URL');
          
          if (hasError) {
            console.log('⚠️ 페이지에 에러 메시지 포함됨');
          } else if (isHtml) {
            console.log('✅ 정상 HTML 응답 수신');
          }
          
          resolve();
        });
      });
      
      req.on('error', (error) => {
        const responseTime = Date.now() - startTime;
        this.results.server.responseTime = responseTime;
        
        console.log(`❌ 서버 연결 실패: ${error.message} (${responseTime}ms)`);
        resolve();
      });
      
      // 10초 타임아웃
      req.setTimeout(10000, () => {
        req.destroy();
        console.log('❌ 서버 연결 타임아웃 (10초)');
        resolve();
      });
    });
  }

  // 4. 요약 리포트
  printSummary() {
    console.log('\n' + '='.repeat(50));
    console.log('테스트 요약 리포트');
    console.log('='.repeat(50));
    
    // .env 파일 상태
    console.log('\n[1] .env 파일:');
    console.log(`   존재: ${this.results.envFile.exists ? '✅' : '❌'}`);
    console.log(`   유효: ${this.results.envFile.valid ? '✅' : '❌'}`);
    
    if (this.results.envFile.content) {
      const lines = this.results.envFile.content.split('\n');
      console.log(`   내용 (${lines.length}줄):`);
      lines.slice(0, 3).forEach(line => {
        if (line.trim()) console.log(`     ${line}`);
      });
      if (lines.length > 3) console.log(`     ... (${lines.length - 3}줄 더)`);
    }
    
    // 로컬 데이터 상태
    console.log('\n[2] 로컬 데이터:');
    console.log(`   존재: ${this.results.localData.exists ? '✅' : '❌'}`);
    console.log(`   유효: ${this.results.localData.valid ? '✅' : '❌'}`);
    console.log(`   항목 수: ${this.results.localData.itemCount}`);
    
    // 서버 연결 상태
    console.log('\n[3] 서버 연결:');
    console.log(`   접속 가능: ${this.results.server.reachable ? '✅' : '❌'}`);
    console.log(`   응답 코드: ${this.results.server.status || 'N/A'}`);
    console.log(`   응답 시간: ${this.results.server.responseTime}ms`);
    
    // 통계
    console.log('\n' + '='.repeat(50));
    
    const passed = [
      this.results.envFile.exists,
      this.results.localData.exists,
      this.results.server.reachable
    ].filter(Boolean).length;
    
    const total = 3;
    
    console.log(`통과: ${passed}/${total}`);
    
    if (passed === total) {
      console.log('🎉 모든 테스트 통과! 시스템 정상입니다.');
    } else if (passed >= 2) {
      console.log('⚠️ 부분 통과. 일부 기능은 작동할 수 있습니다.');
    } else {
      console.log('❌ 대부분의 테스트 실패. 추가 조치 필요.');
    }
    
    // 권장 조치
    console.log('\n권장 조치:');
    
    if (!this.results.envFile.exists) {
      console.log('  1. .env 파일 생성: echo OUTBOUND_GOOGLE_SHEET_URL=... > .env');
    } else if (!this.results.envFile.valid) {
      console.log('  1. .env 파일 수정: OUTBOUND_GOOGLE_SHEET_URL 추가');
    }
    
    if (!this.results.localData.exists) {
      console.log('  2. 로컬 데이터 생성: apply-outbound-fix.bat 실행');
    }
    
    if (!this.results.server.reachable) {
      console.log('  3. 서버 확인:');
      console.log('     - 서버 실행 중인지 확인: npm run dev');
      console.log('     - 방화벽 확인: 포트 5174 열려있는지');
      console.log('     - 네트워크 연결 확인: ping 220.121.225.76');
    }
    
    console.log('='.repeat(50));
  }

  // 메인 실행 함수
  async run() {
    console.log('VF 출고탭 연결 테스트 시작');
    console.log('작업 디렉토리:', process.cwd());
    console.log('='.repeat(50));
    
    // 순차적 테스트 실행
    this.checkEnvFile();
    this.checkLocalDataFile();
    await this.testServerConnection();
    
    // 결과 리포트
    this.printSummary();
  }
}

// 실행
const tester = new OutboundConnectionTester();
tester.run().catch(error => {
  console.error('테스트 실행 중 오류:', error);
  process.exit(1);
});