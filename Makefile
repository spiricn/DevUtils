cwd = $(shell pwd)
out = ${cwd}/out
app_name = du_app
out_app = ${out}/${app_name}

scripts_dir = ${out}/scripts
dst_app_location = /usr/bin/${app_name}
scripts_dist_location = /usr/local/bin/du

all: clean build

clean:
	rm -rfv ${out}

build: build_app build_scripts

build_app:
	${shell bash -c "mkdir -p ${out}"}
	${shell bash -c "${cwd}/archive.sh ${out}/du_app 2>&1 > /dev/null"}
	@echo "created archive: ${out_app}"
	
build_scripts:
	${shell bash -c "mkdir -p ${scripts_dir}"}
	cp -v ${cwd}/bash/*.sh ${scripts_dir}/

install: install_du_app install_scripts

install_scripts:
	${shell bash -c "mkdir -p ${scripts_dist_location}"}
	cp -v ${scripts_dir}/* ${scripts_dist_location}/

install_du_app:
	cp -v ${out_app} /usr/bin/${app_name}
	chmod a+x ${dst_app_location}
