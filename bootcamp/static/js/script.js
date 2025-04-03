// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', function() {
    // 모델 상태 체크
    checkModelStatus();
    
    // 파일 업로드 크기 제한 추가
    setupFileInputs();
    
    // 평가 결과 데이터 테이블 설정 (있는 경우에만)
    setupDataTables();
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
            }
        });
    }
}