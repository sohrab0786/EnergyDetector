##########################################################################
# FILE NAME:  executeidf.sh

# PURPOSE:  Run Simple and Detailed Simulation on Energy Plus Software with 
#           appropriate Input IDF and Weather Files

##########################################################################


#########################Declaration of File PATHS ##########################

flagfilepath="working_directory/"$1"/flagfile.txt"
yes_kill="working_directory/"$1"/sim_killed.txt";
killpid="working_directory/"$1"/pid.txt"

# CALL Process to CHECK IF Simulation IS TO BE KILLED
bash kill_process.sh $1

pwd="working_directory/"$1"/"
rm -f $flagfilepath
basefile= $1
wfile=$2
#wfile="USA_FL_Tampa.Intl.AP.722110_TMY3.epw"
echo "==================================================================="
echo $wfile
echo "==================================================================="

STR1=$1
STR2="base"
echo `date`
STR="working_directory/"$1"/base/model"
echo $STR
PROP="working_directory/"$1"/proposed/model"

echo "this is the base file:"
echo $1

sim1=$pwd"simulated1"
sim2=$pwd"simulated2"

echo "Command: runenergyplus $STR $wfile"
################################################################################

 #Following lines used for transition from 6. to 7.1 (not needed any more
#( transition-V6-0-0-to-V7-0-0 $STR".idf" )
#( transition-V6-0-0-to-V7-0-0 $PROP".idf" )
#( rm -rf $STR".idf" )
#( rm -rf $PROP".idf" )
#( mv $STR".idfnew" $STR".idf" )
#( mv $PROP".idfnew" $PROP".idf" )
#( transition-V7-0-0-to-V7-1-0 $STR".idf" )
#( transition-V7-0-0-to-V7-1-0 $PROP".idf" )
#( rm -rf $STR".idf" )
#( rm -rf $PROP".idf" )
#( mv $STR".idfnew" $STR".idf" )
#( mv $PROP".idfnew" $PROP".idf" )


###### Execute Energy Plus with IDF files as first input and Weather File as second input #######


# Energy Plus simulation for BASE model
# Creation of file 'sim1' denotes completion of simulation 1

( runenergyplus $STR $wfile; touch $sim1 ) &

# Energy Plus simulation for PROPOSED model
# Creation of file 'sim2' denotes completion of simulation 2

( runenergyplus $PROP $wfile; touch $sim2 ) &

###################################################################################################

sleep 3




########## Find PID's of All Process Named "energyplus" ###########
all_process=$(pidof energyplus)

#Create fill "pid.txt" which will be used for storing all to be killed pid's
touch "$killpid"

count=0
for word in $all_process
do
	    count=`expr $count + 1`
	    
	    #Write Pid of last two processes named 'energylus' to pid.txt 
	    #Both these processes belong to this simulation

	    echo "$word " >> "$killpid"
	    if [ $count -eq 2 ]
		then
			break

		fi
done
#####################################################################


########### Find PID's of Find Processes named sh ###################
all_process=$(pidof sh)
count=0
for word in $all_process
do
	    count=`expr $count + 1`
	    #Write Pid of last three processes named 'sh' to pid.txt 
	    echo "$word " >> "$killpid"
	    if [ $count -eq 3 ]
		then
			break

		fi
done
#####################################################################

########### Find PID's of All Processes named runenergyplus ##############
count=0
all_process=$(pidof runenergyplus)
for word in $all_process
do
	    count=`expr $count + 1`
	    #Write Pid of last two processes named 'runenergyplus' to pid.txt 
	    echo "$word " >> "$killpid"
	    if [ $count -eq  2 ]
		then
			break

		fi
done
###########################################################################


##### Sleep till Simulation 1 and 2 have been completed #########
while [ ! -f $sim1 ] || [ ! -f $sim2 ] 
do
	sleep 3
done
#################################################################

#Create Flag File to mark end of executeidf.sh 
touch $flagfilepath
echo "execution Success"