wget https://github.com/PacificBiosciences/HiFi-human-WGS-WDL/releases/download/v2.1.1/hifi-human-wgs-singleton.zip
wget https://github.com/PacificBiosciences/HiFi-human-WGS-WDL/releases/download/v2.1.1/hifi-human-wgs-family.zip

unzip both to wdl folder (merge)
python wdl-container-converter.py --directory wdl --update

```
export MINIWDL__SCHEDULER__CONTAINER_BACKEND=udocker
export MINIWDL__FILE_IO__ALLOW_ANY_INPUT=true
export MINIWDL__SCHEDULER__TASK_CONCURRENCY=1
export UDOCKER_DIR=/scratch/.udocker

miniwdl run wdl/singleton.wdl --dir /scratch --env WORKSPACE_DIR=$WORKSPACE_DIR --runtime-cpu-max=$AGENT_CPU_CORES --runtime-memory-max=${AGENT_MEMORY_GB}G -i wdl/singleton.hpc.inputs.json 
```

L__SCHEDULER__CONTAINER_BACKEND=udocker
        export MINIWDL__FILE_IO__ALLOW_ANY_INPUT=true
        export MINIWDL__SCHEDULER__TASK_CONCURRENCY=1
        export UDOCKER_DIR=/scratch/.udocker
        miniwdl run wdl/singleton.wdl --dir /scratch --env WORKSPACE_DIR=$WORKSPACE_DIR --runtime-cpu-max=$AGENT_CPU_CORES --runtime-memory-max=${AGENT_MEMORY_GB}G -i wdl/singleton.hpc.inputs.json 
        sleep 6h
        # miniwdl run --dir "${WORKFLOW_OUT_DIR}" HiFi-human-WGS-WDL/workflows/singleton.wdl
        # sample_id="$sample_id" hifi_reads="$hifi_reads" ref_map_file="$ref_map_file" backend="$backend"