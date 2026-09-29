pipeline {
    agent {
        label 'windows'   // 需在 Jenkins 里有个 Windows 节点，标签叫 windows
    }

    parameters {
        string(name: 'PARABANK_DIR', defaultValue: 'E:\\parabank-master', description: 'ParaBank 源码目录')
        string(name: 'TEST_SCOPE', defaultValue: 'tests', description: '测试范围（tests / tests/api_test / tests/ui_test）')
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {
        JAVA_HOME = 'D:\\Zulu\\zulu-21'
        PATH      = "D:\\Zulu\\zulu-21\\bin;D:\\apache-maven-3.9.16\\bin;${env.PATH}"
        PYTHONUTF8 = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                echo '===== 拉取测试代码 ====='
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo '===== 安装 Python 依赖 ====='
                bat 'py -m pip install -r requirements.txt'
                bat 'py -m playwright install chromium'
            }
        }

        stage('Build ParaBank') {
            steps {
                echo '===== 构建 ParaBank（生成 WAR） ====='
                bat "cd /d %PARABANK_DIR% && mvn clean package -DskipTests -q"
            }
        }

        stage('Start ParaBank') {
            steps {
                echo '===== 后台启动 ParaBank ====='
                bat """
                    cd /d %PARABANK_DIR%
                    start "parabank" /B cmd /c "mvn cargo:run > parabank.log 2>&1"
                """
                echo '等待 40 秒让服务就绪...'
                sleep 40

                echo '===== 探活 ====='
                bat """
                    curl -s -o nul -w "%%{http_code}" http://localhost:8080/parabank/services/bank/customers/12212/accounts ^
                      -u john:demo > probe.txt
                    set /p CODE=<probe.txt
                    del probe.txt
                    if not "%%CODE%%"=="200" (echo 探活失败: %%CODE%% & exit /b 1)
                """
            }
        }

        stage('Reset Test Data') {
            steps {
                bat 'py scripts\\reset_parabank.py --quiet'
            }
        }

        stage('Run Tests') {
            steps {
                echo '===== 执行测试 ====='
                bat 'py -m pytest %TEST_SCOPE% -q'
            }
        }

        stage('Generate Allure Report') {
            steps {
                bat 'allure generate allure-results --clean -o allure-report'
            }
        }
    }

    post {
        always {
            echo '===== 归档产物 ====='
            junit 'test-results/junit.xml'
            archiveArtifacts artifacts: 'allure-results/**', allowEmptyArchive: true
            archiveArtifacts artifacts: 'test-results/**', allowEmptyArchive: true

            publishHTML(target: [
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'allure-report',
                reportFiles: 'index.html',
                reportName: 'Allure Test Report'
            ])

            echo '===== 停止 ParaBank ====='
            bat '''
                for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080" ^| findstr LISTENING') do taskkill /F /PID %%a
            '''
        }
        failure {
            echo '===== 失败保留浏览器截图 + Trace ====='
            archiveArtifacts artifacts: 'test-results/**/*.png', allowEmptyArchive: true
            archiveArtifacts artifacts: 'test-results/**/*.zip', allowEmptyArchive: true
        }
    }
}