pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
    }

    environment {
        REGISTRY_REPO = 'dina98942/fintrack-account-service'
        DOCKER_CREDENTIALS = 'dockerhub-creds'

        K8S_NAMESPACE = 'fintrack'
        DEPLOYMENT = 'account-service-v2'
        CONTAINER = 'account-service'
        SERVICE = 'account-service'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm

                script {
                    env.IMAGE_TAG = sh(
                        script: 'git rev-parse --short=12 HEAD',
                        returnStdout: true
                    ).trim()

                    env.IMAGE = "${REGISTRY_REPO}:${env.IMAGE_TAG}"
                    
                    echo "Commit: ${env.GIT_COMMIT}"
                    echo "Immutable image: ${env.IMAGE}"
                }
            }
        }

        stage('Test Application') {
            steps {
                sh '''
                    set -eu

                    test -f docker/account-service/app/server.py
                    test -f docker/account-service/Dockerfile

                    grep -q '"/health"' docker/account-service/app/server.py
                    grep -q '"/version"' docker/account-service/app/server.py

                    echo "Application source checks passed"
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    set -eu

                    echo "Building ${IMAGE}"

                    docker build \
                      --pull \
                      -t "${IMAGE}" \
                      docker/account-service

                    docker image inspect "${IMAGE}" >/dev/null

                    echo "Docker build successful"
                '''
            }
        }

stage('Docker Push') {
    steps {
        withCredentials([
            usernamePassword(
                credentialsId: "${DOCKER_CREDENTIALS}",
                usernameVariable: 'DOCKER_USERNAME',
                passwordVariable: 'DOCKER_PASSWORD'
            )
        ]) {
            sh '''
                set -eu

                echo "${DOCKER_PASSWORD}" | docker login \
                  --username "${DOCKER_USERNAME}" \
                  --password-stdin

                docker push "${IMAGE}"

                docker logout
            '''
        }

        script {
            env.IMAGE = "${REGISTRY_REPO}:rollback-test-nonexistent-c751cdc"
            echo "Intentional rollback test image: ${env.IMAGE}"
        }
    }
}
        stage('Capture Current Image') {
            steps {
                script {
                    env.PREVIOUS_IMAGE = sh(
                        script: """
                            kubectl -n ${K8S_NAMESPACE} \
                              get deployment ${DEPLOYMENT} \
                              -o jsonpath='{.spec.template.spec.containers[0].image}'
                        """,
                        returnStdout: true
                    ).trim()

                    if (!env.PREVIOUS_IMAGE) {
                        error("Could not determine current deployment image")
                    }

                    echo "Current deployed image: ${env.PREVIOUS_IMAGE}"
                    echo "New image: ${env.IMAGE}"
                }
            }
        }

        stage('Deploy and Verify Canary') {
            steps {
                script {

                    try {

                        sh '''
                            set -eu

                            echo "Deploying ${IMAGE}"

                            kubectl -n "${K8S_NAMESPACE}" \
                              set image deployment/"${DEPLOYMENT}" \
                              "${CONTAINER}"="${IMAGE}"

                            kubectl -n "${K8S_NAMESPACE}" \
                              rollout status deployment/"${DEPLOYMENT}" \
                              --timeout=180s
                        '''

                        sh '''
                            set -eu

                            echo "Checking deployed image..."

                            CURRENT_IMAGE=$(kubectl -n "${K8S_NAMESPACE}" \
                              get deployment "${DEPLOYMENT}" \
                              -o jsonpath='{.spec.template.spec.containers[0].image}')

                            echo "Current image: ${CURRENT_IMAGE}"

                            test "${CURRENT_IMAGE}" = "${IMAGE}"

                            echo "Deployment image verification passed"
                        '''

                        sh '''
                            set -eu

                            echo "Checking deployment availability..."

                            kubectl -n "${K8S_NAMESPACE}" \
                              get deployment "${DEPLOYMENT}"

                            AVAILABLE=$(kubectl -n "${K8S_NAMESPACE}" \
                              get deployment "${DEPLOYMENT}" \
                              -o jsonpath='{.status.availableReplicas}')

                            echo "Available replicas: ${AVAILABLE}"

                            test "${AVAILABLE}" -ge 1

                            echo "Deployment availability check passed"
                        '''

                        sh '''
                            set -eu

                            echo "Checking Istio routing..."

                            kubectl -n "${K8S_NAMESPACE}" \
                              get virtualservice "${SERVICE}" -o yaml
                        '''

                        sh '''
                            set -eu

                            echo "Checking v1/v2 pods..."

                            kubectl -n "${K8S_NAMESPACE}" \
                              get pods -l app=account-service -o wide
                        '''

                        echo "Canary deployment and verification succeeded"

                    } catch (err) {

                        echo "CANARY DEPLOYMENT FAILED"
                        echo "Starting automatic rollback..."
                        echo "Rollback target: ${env.PREVIOUS_IMAGE}"

                        sh '''
                            set -eu

                            kubectl -n "${K8S_NAMESPACE}" \
                              set image deployment/"${DEPLOYMENT}" \
                              "${CONTAINER}"="${PREVIOUS_IMAGE}"

                            kubectl -n "${K8S_NAMESPACE}" \
                              rollout status deployment/"${DEPLOYMENT}" \
                              --timeout=180s

                            echo "Rollback completed"
                        '''

                        sh '''
                            set -eu

                            ROLLBACK_IMAGE=$(kubectl -n "${K8S_NAMESPACE}" \
                              get deployment "${DEPLOYMENT}" \
                              -o jsonpath='{.spec.template.spec.containers[0].image}')

                            echo "Image after rollback: ${ROLLBACK_IMAGE}"

                            test "${ROLLBACK_IMAGE}" = "${PREVIOUS_IMAGE}"

                            echo "Rollback verification passed"
                        '''

                        echo "Automatic rollback restored the previous image"

                        throw err
                    }
                }
            }
        }
    }

    post {
        success {
            echo "FinTrack deployment succeeded: ${env.IMAGE}"
        }

        failure {
            echo "FinTrack deployment failed. Automatic rollback was attempted if deployment had started."
        }

        always {
            sh '''
                docker logout >/dev/null 2>&1 || true
            '''
        }
    }
}
