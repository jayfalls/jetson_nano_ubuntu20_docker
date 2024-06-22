#!/usr/bin/env python3

# DEPENDENCIES
## Built-In
import os
from typing import Optional
## Third-Party
import inquirer
import onnx
from onnx import (
    helper,
    GraphProto, ModelProto, NodeProto, TensorProto
)


# STARTUP
def find_models() -> frozenset[str]:
    return frozenset(os.path.join(root, f) for root, _, files in os.walk('.') for f in files if f.endswith('.onnx'))

# MODIFICATIONS
def remove_topk(model_path: str) -> None:
    model: ModelProto = onnx.load(model_path)
    graph: GraphProto = model.graph

    last_transpose_node: Optional[NodeProto] = None
    for node in reversed(graph.node):
        if node.op_type == 'Transpose':
            last_transpose_node = node
            break

    if not last_transpose_node:
        raise ValueError("No Transpose node found in the model")

    transpose_input: str = last_transpose_node.input[0]

    nodes_to_keep: list[NodeProto] = []
    for node in graph.node:
        if node == last_transpose_node:
            break
        nodes_to_keep.append(node)

    graph.output[0].name = transpose_input
    graph.output[0].type.tensor_type.elem_type = onnx.TensorProto.FLOAT

    graph.ClearField("node")
    graph.node.extend(nodes_to_keep)

    output_path: str = model_path.replace('.onnx', '_topk_removed.onnx')
    onnx.save(model, output_path)
    print(f"Model successfully saved to {output_path}")

def replace_mod_with_supported_ops(model_path: str) -> None:
    model: ModelProto = onnx.load(model_path)
    graph: GraphProto = model.graph

    mod_node: Optional[NodeProto] = next((node for node in graph.node if node.op_type == 'Mod'), None)
    if not mod_node:
        print("No Mod node found")
        return

    input_name: str = mod_node.input[0]
    output_name: str = mod_node.output[0]

    cast_input_node: NodeProto = helper.make_node('Cast', [input_name], ['float_input'], to=TensorProto.FLOAT)

    div_node: NodeProto = helper.make_node('Div', ['float_input', 'modulus'], ['div_output'])
    floor_node: NodeProto = helper.make_node('Floor', ['div_output'], ['floor_output'])
    mul_node: NodeProto = helper.make_node('Mul', ['modulus', 'floor_output'], ['mul_output'])
    sub_node: NodeProto = helper.make_node('Sub', ['float_input', 'mul_output'], ['float_output'])

    cast_output_node: NodeProto = helper.make_node('Cast', ['float_output'], [output_name], to=TensorProto.INT32)

    modulus: float = 80.0 # The number of classes in the model
    modulus_tensor: TensorProto = helper.make_tensor('modulus', TensorProto.FLOAT, [1], [modulus])
    graph.initializer.append(modulus_tensor)

    graph.node.remove(mod_node)
    graph.node.extend([cast_input_node, div_node, floor_node, mul_node, sub_node, cast_output_node])

    output_path: str = model_path.replace('.onnx', '_modulus_replaced.onnx')
    onnx.save(model, output_path)
    print(f"Model successfully saved to {output_path}!")


# MAIN
def main() -> None:
    print("\nWARNING!!! This can break any non v10 models!\n")
    models: frozenset[str] = find_models()
    
    model_questions: list[inquirer.List]  = [
        inquirer.List(
            "selection",
            message="Select a yolov10 model to make tensorrt compatible with the Jetson Nano...",
            choices=sorted(models, reverse=True)
        ),
    ]

    model_type: dict[str, str] | None = inquirer.prompt(model_questions)
    if not model_type:
        raise ValueError("No action selected!")
    if not model_type.get("selection", None):
        raise ValueError("Invalid model selection!")
    model_selection: str = model_type["selection"]

    class ActionTypes:
        MODULUS_REPLACE: str = "Basic Compatibility"
        TOPK_REMOVE: str = "I want my model to go as fast as possible! WARNING!!! This removes TopK (NMS) from the model and can result in a ton of overlapping detections!"
    action_types: tuple[str, str] = (
        ActionTypes.MODULUS_REPLACE,
        ActionTypes.TOPK_REMOVE
    )

    action_questions: list[inquirer.List] = [
        inquirer.List(
            "selection",
            message="Select an action to perform on the v10 model...",
            choices=action_types
        ),
    ]

    action_type: dict[str, str] | None = inquirer.prompt(action_questions)
    if not action_type:
        raise ValueError("No action selected!")
    if not action_type.get("selection", None):
        raise ValueError("Invalid action selection!")
    action_selection: str = action_type["selection"]

    if action_selection == ActionTypes.MODULUS_REPLACE:
        replace_mod_with_supported_ops(model_selection)
    elif action_selection == ActionTypes.TOPK_REMOVE:
        remove_topk(model_selection)

if __name__ == "__main__":
    main()
