cwd = $(shell pwd)
out = ${cwd}/out
app_name = "du_app"
out_app = "${out}/${app_name}"

all: clean archive

clean:
	rm -rfv ${out}

archive:
	${shell bash -c "mkdir -p ${out}"}
	${shell bash -c "${cwd}/archive.sh ${out}/du_app 2>&1 > /dev/null"}
	@echo "created archive: ${out_app}"

install:
	cp ${out_app} /usr/bin/${app_name}