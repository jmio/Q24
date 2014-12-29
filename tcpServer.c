/* tcpServer.c - Tiny HTTP Server
 * This code is from vxWorksTCP server example */

/* includes */ 
#include "vxWorks.h" 
#include "sockLib.h" 
#include "inetLib.h" 
#include "taskLib.h" 
#include "stdioLib.h" 
#include "strLib.h" 
#include "ioLib.h" 
#include "fioLib.h" 
/* define __PROTOTYPE_5_0 for Clear logMsg prototype error */
#define __PROTOTYPE_5_0
#include <logLib.h>
#include <stdlib.h>
#include <sys/stat.h>

/* defines */ 
#define SERVER_PORT_NUM         80     /* server's port number for bind() */ 
#define SERVER_WORK_PRIORITY    100    /* priority of server's work task */ 
#define SERVER_STACK_SIZE       10000  /* stack size of server's work task */ 
#define SERVER_MAX_CONNECTIONS  4      /* max clients connected at a time */ 
#define REQUEST_MSG_SIZE        8192   /* max size of request message */ 
#define REPLY_MSG_SIZE          8192   /* max size of reply message */ 

static
char NOTFOUNDMSG[] =
	"<html><head><title>Not Found</title></head><body style=\"font-family:verdana,tahoma,sans-serif\">\n"
	"<h1 style=\"color:#FF0000\">404</h1>\n"
	"The requested resource is not registered or cannot be served.<br>\n"
	"<hr>\n<address>Embedded HTTP server</address>\n"
	"</body></html>\n";


static
char SERVERERRMSG[] =
	"<html><head><title>Server Error</title></head><body style=\"font-family:verdana,tahoma,sans-serif\">\n"
	"<h1 style=\"color:#FF0000\">501</h1>\n"
	"Server Error.<br>\n"
	"<hr>\n<address>Embedded HTTP server</address>\n"
	"</body></html>\n";

/*
 * copy source to destination with max toklen
 */
char* gettoken(char *s,char *d,int len)
{
	char c ;

	/* skip space */
	while((c = *s++) != 0)
	{
		/* if detect not white space then break */
		if (c > ' ') {
			s-- ;
			break ;
		}
		if ((c != '\t') && (c != ' ')) {
			/* add end mark */
			*d = '\0' ;
			return s ;
		}
	}
	
	/* copy char */
	while(((c = *s++) != 0) && (len-- > 0))
	{
		/* if detect white space , then end copy */
		if (c <= ' ') {
			break ;
		}
		*d++ = c ;
	}

	/* add end mark */
	*d = '\0' ;
	return s ;
}

/* function declarations */
VOID tcpServerWorkTask (int sFd, in_addr_t address, u_short port);

/**************************************************************************** 
* 
* tcpServer - accept and process requests over a TCP socket 
* Derived from vxWorks tcpServer Sample
* 
*/

STATUS tcpServer (void) 
{ 
	struct sockaddr_in  serverAddr;    /* server's socket address */ 
	struct sockaddr_in  clientAddr;    /* client's socket address */ 
	int                 sockAddrSize;  /* size of socket address structure */ 
	int                 sFd;           /* socket file descriptor */ 
	int                 newFd;         /* socket descriptor from accept */ 
	int                 ix = 0;        /* counter for work task names */ 
	char                workName[16];  /* name of work task */
	/* set up the local address */

	sockAddrSize = sizeof (struct sockaddr_in); 
	bzero ((char *) &serverAddr, sockAddrSize); 
	serverAddr.sin_family = AF_INET; 
	serverAddr.sin_len = (u_char) sockAddrSize; 
	serverAddr.sin_port = htons (SERVER_PORT_NUM); 
	serverAddr.sin_addr.s_addr = htonl (INADDR_ANY);

	/* create a TCP-based socket */

	if ((sFd = socket (AF_INET, SOCK_STREAM, 0)) == ERROR) 
	    { 
	    perror ("socket"); 
	    return (ERROR); 
	    }

	/* bind socket to local address */

	if (bind (sFd, (struct sockaddr *) &serverAddr, sockAddrSize) == ERROR) 
	    { 
	    perror ("bind"); 
	    close (sFd); 
	    return (ERROR); 
	    }

	/* create queue for client connection requests */

	if (listen (sFd, SERVER_MAX_CONNECTIONS) == ERROR) 
	    { 
	    perror ("listen"); 
	    close (sFd); 
	    return (ERROR); 
	    }

	/* accept new connect requests and spawn tasks to process them */

	FOREVER 
	    { 
	    if ((newFd = accept (sFd, (struct sockaddr *) &clientAddr, 
	        &sockAddrSize)) == ERROR) 
	        { 
	        perror ("accept"); 
	        close (sFd); 
	        return (ERROR); 
	        }

	    sprintf (workName, "tTcpWork%d", ix++); 
	    if (taskSpawn(workName, SERVER_WORK_PRIORITY, 0, SERVER_STACK_SIZE, 
	        (FUNCPTR) tcpServerWorkTask, newFd, 
	        (int)clientAddr.sin_addr.s_addr , ntohs (clientAddr.sin_port), 
	        0, 0, 0, 0, 0, 0, 0) == ERROR) 
	        { 
	        /* if taskSpawn fails, close fd and return to top of loop */ 

	        perror ("taskSpawn"); 
	        close (newFd); 
	        } 
	    } 
} 

/**************************************************************************** 
* 
* tcpServerWorkTask - process client requests 
* 
* This routine reads from the server's socket, and processes client 
* requests.  If the client requests a reply message, this routine 
* will send a reply to the client. 
* 
* RETURNS: N/A. 
*/ 

void http_send_const(int sFd,char *str,int resultcode) ;
void http_page_send(int fd,char *fname) ;

VOID tcpServerWorkTask 
( 
	int                 sFd,            /* server's socket fd */ 
	in_addr_t           address,        /* client's socket address */ 
	u_short             port            /* client's socket port */ 
) 
{
	int i;
	char      clientRequest[REQUEST_MSG_SIZE];  /* request/message from client */ 
	int                 nRead;          /* number of bytes read */ 
	char method[128] ;
	char fpath[256] ;
		
	/* read client request, display message */
	nRead = 0;
	while(nRead == 0) {
    	if ( ioctl(sFd, FIONREAD, (int)&nRead) < 0 ) {
        	perror("HTTPD: ioctl() < 0\n");
        	return ;
    	}
		taskDelay(10);
	}

	read(sFd, (char *) &clientRequest,nRead) ;
	printf ("CLIENT (Internet Address %08x, port %d):%d\n", 
	             address, port,nRead); 
	printf("\n---------\n");
	for(i=0;i<nRead;i++)
	{
		char c = clientRequest[i] ;
		if (c >= ' ') {
			printf("%c",c);
		} else {
			printf("[%02X]",c);
			if (c == '\n') {
				printf("\n");
			}
		}
	}
	printf("\n---------\n");
	
	{
		char *p = &clientRequest[0] ;
		p = gettoken(p,method,100) ;
		p = gettoken(p,fpath,100) ;		
	}
	printf("Method:%s\n",method);
	printf("PATH:%s\n",fpath);
	
	http_page_send(sFd,fpath);
	close (sFd);                        
}

void http_send_header(int sFd,int len,int resultcode,char *filetype)
{
	char *buffer;
	buffer = (char *)malloc(255) ;
	bzero(buffer, 255);
	sprintf(buffer, 
			"HTTP/1.1 %d OK\n"
			"Content-Type: %s\n"
			"Content-Length: %d\n"
			"Connection: close\n"
			"\n",
		resultcode,
		filetype,
		len);
	write(sFd,buffer,strlen(buffer));
	free(buffer);
}

void http_send_const(int sFd,char *str,int resultcode)
{
	http_send_header(sFd,strlen(str),resultcode,"text/html");
	write(sFd,str,strlen(str));
}

#define INDEXFILE "/index.html"
void http_page_send(int fd,char *fname)
{
    char *r;
	int l ;
	FILE *f ;
    struct stat stbuf;

    stat(fname, &stbuf);
    l = stbuf.st_size;
    if (!S_ISREG(stbuf.st_mode)) {
        /* if Directory, add index and retry */
    	if (S_ISDIR(stbuf.st_mode)) {
			r = malloc(strlen(fname)+strlen(INDEXFILE)+10) ;
			if (r) {
				strcpy(r,fname);
				strcat(r,INDEXFILE);
				http_page_send(fd,r);
				free(r);
				return ;
			}
    	}
    	
    	/* is not normal file... */
		http_send_const(fd,NOTFOUNDMSG,404);
		return ;    	
    } 
    
    f = fopen(fname,"rb");
    if (!f) {
		http_send_const(fd,NOTFOUNDMSG,404);
		return ;
    }
    r = (char *)malloc(l);
	if (r) {
	    fread(r,1,l,f);
		http_send_header(fd,l,200,"text/html");
		write(fd,r,l);
		free(r);
	} else {
		http_send_const(1,SERVERERRMSG,501);
	}
    fclose(f);
}
