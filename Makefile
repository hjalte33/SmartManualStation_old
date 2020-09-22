pi:
	rsync -r -e 'ssh -J remote.moe' ./ pi@smartmanualstation.remote.moe:SmartManualStation

piclean: 
	rsync -r --delete -e 'ssh -J remote.moe' ./ pi@smartmanualstation.remote.moe:SmartManualStation