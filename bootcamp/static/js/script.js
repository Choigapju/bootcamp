// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', function() {
    // 모델 상태 체크
    checkModelStatus();
    
    // 파일 업로드 크기 제한 추가
    setupFileInputs();
    
    // 평가 결과 데이터 테이블 설정 (있는 경우에만)
    setupDataTables();
    
    // 점수 색상 적용
    applyScoreColors();
});

// 모델 상태 확인
function checkModelStatus() {
    fetch('/model_info')
        .then(response => response.json())
        .then(data => {
            // 상태 정보를 받아 표시할 수 있음
            console.log('모델 상태:', data);
        })
        .catch(error => {
            console.error('모델 상태 확인 중 오류:', error);
        });
}

// 파일 업로드 입력 설정
function setupFileInputs() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.files.length > 0) {
                const fileSize = this.files[0].size / 1024 / 1024; // MB로 변환
                if (fileSize > 10) { // 10MB 제한
                    alert('파일 크기가 10MB를 초과합니다. 더 작은 파일을 선택해주세요.');
                    this.value = '';
                }
                
                // 파일 이름 표시
                const fileNameElement = document.createElement('div');
                fileNameElement.className = 'mt-2 text-info';
                fileNameElement.textContent = `선택된 파일: ${this.files[0].name}`;
                
                // 이전 파일 이름 표시 제거
                const prevFileName = this.parentElement.querySelector('.text-info');
                if (prevFileName) {
                    prevFileName.remove();
                }
                
                this.parentElement.appendChild(fileNameElement);
            }
        });
    });
}

// 데이터 테이블 설정 (결과 페이지)
function setupDataTables() {
    const resultTables = document.querySelectorAll('.table-responsive table');
    if (resultTables.length > 0 && typeof $.fn.DataTable !== 'undefined') {
        $(resultTables).DataTable({
            responsive: true,
            pageLength: 10,
            lengthMenu: [5, 10, 25, 50],
            language: {
                search: "검색:",
                lengthMenu: "_MENU_ 개씩 보기",
                paginate: {
                    first: "처음",
                    last: "마지막",
                    next: "다음",
                    previous: "이전"
                },
                info: "_TOTAL_ 개 중 _START_ - _END_",
                infoEmpty: "0 개 중 0 - 0",
                infoFiltered: "(전체 _MAX_ 개에서 필터링됨)",
                zeroRecords: "일치하는 레코드가 없습니다"
            },
            // 테이블 렌더링 후 점수 색상 적용
            initComplete: function() {
                applyScoreColors();
            }
        });
    }
}

// 점수에 따른 색상 적용 함수
function applyScoreColors() {
    try {
        console.log("점수 색상 적용 시작");
        
        // 테이블의 모든 행 가져오기
        const tableRows = document.querySelectorAll('table tbody tr');
        
        // 컬럼 인덱스 결정 (테이블 구조에 따라 조정 필요)
        let scoreColumnIndex = 3; // 점수 열 (기본값)
        let probabilityColumnIndex = 4; // 학률 열 (기본값)
        
        // 테이블 헤더 확인하여 인덱스 조정
        const headers = document.querySelectorAll('table thead th');
        headers.forEach((header, index) => {
            const headerText = header.textContent.trim().toLowerCase();
            if (headerText === '점수') {
                scoreColumnIndex = index;
            } else if (headerText === '학률') {
                probabilityColumnIndex = index;
            }
        });
        
        console.log(`점수 열 인덱스: ${scoreColumnIndex}, 학률 열 인덱스: ${probabilityColumnIndex}`);
        
        // 각 행에 색상 적용
        tableRows.forEach(row => {
            // 점수(점수) 열에 색상 적용
            const scoreCell = row.cells[scoreColumnIndex];
            if (scoreCell) {
                const score = parseFloat(scoreCell.textContent);
                if (!isNaN(score)) {
                    // 점수에 따른 클래스 추가
                    if (score >= 6.0) {
                        scoreCell.classList.add('final-score-high');
                    } else if (score >= 4.0) {
                        scoreCell.classList.add('final-score-medium');
                    } else {
                        scoreCell.classList.add('final-score-low');
                    }
                }
            }
            
            // 학률(확률) 열에 색상 적용
            const probabilityCell = row.cells[probabilityColumnIndex];
            if (probabilityCell) {
                const probability = parseFloat(probabilityCell.textContent);
                if (!isNaN(probability)) {
                    // 확률에 따른 클래스 추가
                    if (probability >= 0.4) {
                        probabilityCell.classList.add('score-high');
                    } else if (probability >= 0.3) {
                        probabilityCell.classList.add('score-medium');
                    } else {
                        probabilityCell.classList.add('score-low');
                    }
                }
            }
            
            // 상태 열이 있는 경우 (상태 컬럼 인덱스 찾기)
            headers.forEach((header, index) => {
                const headerText = header.textContent.trim().toLowerCase();
                if (headerText === '상태') {
                    const statusCell = row.cells[index];
                    if (statusCell) {
                        const status = statusCell.textContent.trim();
                        if (status === '합격') {
                            statusCell.classList.add('status-pass');
                        } else if (status === '면접대상') {
                            statusCell.classList.add('status-interview');
                        } else if (status === '불합격') {
                            statusCell.classList.add('status-fail');
                        }
                    }
                }
            });
        });
        
        console.log("점수 색상 적용 완료");
    } catch (error) {
        console.error("점수 색상 적용 중 오류 발생:", error);
    }
}

// 테이블이 동적으로 변경될 때 (페이지네이션, 정렬 등) 색상 다시 적용
document.addEventListener('DOMNodeInserted', function(event) {
    // 테이블 행이 추가된 경우에만 처리
    if (event.target && event.target.nodeName === 'TR') {
        setTimeout(applyScoreColors, 50); // 약간의 지연을 두고 적용
    }
});