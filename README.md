BSA Assignment Version 1.0

## Getting Started

The program can be also started by using docker container service. 
The following steps can be used to run the code as a container after cloning the respository.

```bash
$ docker build -t bsa_assignment_image .
$ docker run -p 8080:8000 -d --name bsa_assignment_container bsa_assignment_image
```

## Author

Please create own branches to work on your particular task and maintain best practices like 
openning PRs and responding review comment etc.
Regards
Saptarshi Pal