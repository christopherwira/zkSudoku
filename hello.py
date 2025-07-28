from utils import zokrates_utils
import json

zokrates_utils.compile_zokrates_script('hello')
zokrates_utils.generate_proving_verification_key_with_trusted_setup('hello')
zokrates_utils.check_keys_size('hello')
hello_dict = ["337", "113569"]
zokrates_utils.generate_proof_from_json_input('hello',json.dumps(hello_dict))
print(zokrates_utils.verify_proof('hello'))
