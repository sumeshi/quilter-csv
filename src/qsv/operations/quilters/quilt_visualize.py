from qsv.controllers.QuiltController import QuiltController

def quilt_visualize(config: str):
    q = QuiltController()
    configs = q.load_configs(config)

    for config in configs:

        mermaid = list()
        mermaid.append(f'---\ntitle: {config.get("title", "Pipeline")}\n---')
        mermaid.append('stateDiagram-v2')
        stages = config.get('stages')

        for stage_key, stage_values in stages.items():

            # stage -> stage
            if not (stage_values.get('source') or stage_values.get('sources')):
                mermaid.append(f'[*] --> {stage_key}')
            else:
                source = stage_values.get('source')
                if source:
                    mermaid.append(f'{source} --> {stage_key}')
                
                sources = stage_values.get('sources')
                if sources:
                    for s in sources:
                        mermaid.append(f'{s} --> {stage_key}')

            # inner-stage operations
            mermaid.append(f'state {stage_key}' + '{')

            stage_type = stage_values.get('type')
            if stage_type == 'process':
                steps = stage_values.get('steps')
                recent = None
                for k, v in steps.items():
                    if len(steps):
                        mermaid.append(f"  {k}@{stage_key}")
                    if recent:
                        mermaid.append(f"  {recent}@{stage_key} --> {k}@{stage_key}")
                    recent = k
            else:
                mermaid.append(f"{stage_values.get('type')}@{stage_key}")

            mermaid.append('}')
        
        else:
            mermaid.append(f"{stage_key} --> [*]")

        print("\n".join(mermaid))
