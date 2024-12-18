# 작업 이력
## metal lb 설치



## metal lb 설치 이력
- 설치 과정 중 에러 발생으로 CrashLoopBackOff 발생 중
- error log는 아래와 같음
```Bash
Defaulted container "speaker" out of: speaker, frr, reloader, frr-metrics, cp-frr-files (init), cp-reloader (init), cp-metrics (init)
{"branch":"dev","caller":"main.go:107","commit":"dev","goversion":"gc / go1.21.9 / amd64","level":"info","msg":"MetalLB speaker starting version 0.14.5 (commit dev, branch dev)","ts":"2024-10-25T05:05:00Z","version":"0.14.5"}
{"caller":"speakerlist.go:98","error":"Could not set up network transport: failed to obtain an address: Failed to start TCP listener on \"192.168.0.110\" port 7946: listen tcp 192.168.0.110:7946: bind: address already in use","level":"error","msg":"failed to create memberlist","op":"startup","ts":"2024-10-25T05:05:00Z"}
```
- worker 노드의 7946 port를 사용중이어서 문제가 발생하는 것 같음
- worker 노드에서 7946 port를 사용하는 것은 아이러니하게 metallb임
```Bash
clouflake@matgo-k8s-worker:~$ sudo lsof -i :7946
[sudo] password for clouflake:
COMMAND    PID USER   FD   TYPE  DEVICE SIZE/OFF NODE NAME
speaker 563827 root    8u  IPv4 1803339      0t0  TCP matgo-k8s-worker:7946 (LISTEN)
speaker 563827 root    9u  IPv4 1803343      0t0  UDP matgo-k8s-worker:7946
```
- 원인 상세 파악 필요할듯
- 비슷한 문제를 해결한 [링크](https://github.com/metallb/metallb/issues/1539) 
- 문제를 해결 했음 해결 과정은 아래와 같음
  1. 지속적으로 address already in use가 발생해서 110 서버의 노드로 접속을 했음
  2. 접속해서 실제로 포트가 사용중인지 `netstat -an | grep 7946`  `sudo lsof -i :7946` 로 확인해보니까 아래와 같았음
  ```Bash
    clouflake@matgo-k8s-worker:~$ sudo netstat -tuln | grep 7946
    tcp        0      0 192.168.0.110:7946      0.0.0.0:*               LISTEN
    udp        0      0 192.168.0.110:7946      0.0.0.0:*
  ```
  ```Bash
    clouflake@matgo-k8s-worker:~$ sudo lsof -i :7946
    COMMAND    PID USER   FD   TYPE  DEVICE SIZE/OFF NODE NAME
    speaker 563827 root    8u  IPv4 1803339      0t0  TCP matgo-k8s-worker:7946 (LISTEN)
    speaker 563827 root    9u  IPv4 1803343      0t0  UDP matgo-k8s-worker:7946
  ```
  3. 분명히 helm uninstall로 삭제를 하고 pod 목록에도 없는데 worker node에는 프로세스가 살아있는 것을 알 수 있었고, SIGTERM 명령을 날려서 삭제를 진행함
  4. 삭제 후 helm install로 재설치를 진행했는데 해결이 됨...
  ```Bash
    metallb-system    metallb-controller-65d44888b9-dj67h                 1/1     Running       0                51s
    metallb-system    metallb-speaker-6vfrq                               1/1     Running       0                51s
    metallb-system    metallb-speaker-jhrfn                               1/1     Running       0                51s
  ```
  5. 서비스도 문제 없이 metallb의 range에 맞게 할당됨



## longhorn 설치
- _설치 과정중 ingress 제외함_ (원한다면 [링크](https://longhorn.io/docs/1.5.5/deploy/accessing-the-ui/longhorn-ingress/)에서 설정 가능)
- longhorn-system 네임 스페이스에 생성