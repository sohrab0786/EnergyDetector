##########################################################################
# FILE NAME:  kill_process.sh

# PURPOSE:  Kill all processes related to a simulation
#           if an exact match for inputs is found in
#	    database

##########################################################################

# Delaration of File Paths
yes_kill="working_directory/"$1"/sim_killed.txt";
no_kill="working_directory/"$1"/sim_not_killed.txt";
killpid="working_directory/"$1"/pid.txt"

####### Checking if Simulation is to be "KILLED" or "NOT KILLED" ########
flag=1
while [ ! -f $yes_kill ]
do
	if [ -f $no_kill ]
	then	
	
		# Exit Code if Simulation is not to be killed
		flag=0
		exit 0
		break
	fi

	sleep 1
done
#########################################################################

#### Waiting for Creation of file 'pid.txt' 
while [ ! -f $killpid ]
do
	sleep 1
done

#WAIT CUSHION FOR executeidf.sh to write to pid.txt
sleep 5

########### Kill all Processes related to this simulation ############## 
if [ $flag -eq 1 ] 
then 
# Read from file "pid.txt"
while read p;
do
	echo "PROCESS ENERGY PLUS TERMINATED with pid "$p
	# KILL Process with pid "$p"
	kill $p
done < $killpid

fi

#########################################################################
