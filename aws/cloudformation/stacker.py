#!/usr/bin/env python

from __future__ import print_function
from boto import (cloudformation, s3, exception)
import argparse
import time

class Stacker():
    def __init__(self, region):
        self.region = region
        self.cf = cloudformation.connect_to_region(self.region)

    def list_stacks(self):
        self.successful_filter = ["UPDATE_COMPLETE", "CREATE_COMPLETE"]
        self.failed_filter = ["CREATE_FAILED", "UPDATE_ROLLBACK_FAILED",
                              "DELETE_FAILED", "ROLLBACK_FAILED",
                              "ROLLBACK_IN_PROGRESS", "ROLLBACK_COMPLETE",
                              "UPDATE_ROLLBACK_COMPLETE"]
        self.update_filter = ["UPDATE_ROLLBACK_FAILED",
                              "UPDATE_ROLLBACK_IN_PROGRESS",
                              "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS",
                              "UPDATE_COMPLETE","UPDATE_IN_PROGRESS",
                              "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS",
                              "UPDATE_ROLLBACK_COMPLETE"]

        successful_stacks = self.cf.list_stacks(stack_status_filters=self.successful_filter)
        failed_stacks = self.cf.list_stacks(stack_status_filters=self.failed_filter)
        update_stacks = self.cf.list_stacks(stack_status_filters=self.update_filter)

        print("Successful CloudFormation Stacks:")
        for stack in successful_stacks:
            print(stack.stack_name)

        print("Failed CloudFormation Stacks:")
        for stack in failed_stacks:
            print(stack.stack_name)

        print("Update CloudFormation Stacks:")
        for stack in update_stacks:
            print(stack.stack_name)

    def upload_template(self, local_template):
        self.bucket = 'cf-templates-158gc87u1eu1y-us-east-1'
        self.local_template = local_template
        self.template = self.local_template.replace('/home/mike/', '')

        print("Uploading new template file to s3")
        self.conn = s3.connect_to_region('us-east-1')
        try:
            b = self.conn.get_bucket(self.bucket)
            k = s3.key.Key(b)
            k.key = self.template
            k.set_contents_from_filename(self.local_template)
            #k.close
        except:
            print("Failed uploading the new template to s3")
        finally:
            template_url = "http://s3.amazonaws.com/" + self.bucket + "/" + self.template
        return template_url

    def create_stack(self, stack_name, template):
        self.stack_name = stack_name
        self.template = template
        try:
            print("Creating a new stack using template: " + self.template)
            self.cf.create_stack(self.stack_name, template_url=self.template)
        except exception.BotoServerError as e:
            print("Failed creating stack using template: " + self.template)
            print(e)

        print("Getting stack creation status...")
        while True:
            time.sleep(15)
            try:
                self.status = self.cf.describe_stack_events(stack_name_or_id=self.stack_name)
            finally:
                self.status.reverse()
                if "Stack " + self.stack_name + " CREATE_COMPLETE" in str(self.status):
                    print("Creation of the stack " + self.stack_name + " complete.")
                    break

    def delete_stack(self, stack_name):
        self.stack_name = stack_name


if __name__ == "__main__":
    s = Stacker('us-east-1')
    stacks = s.list_stacks()
    print(stacks)

    # upload local file to s3 bucket and then reference the file via s3 web url
    #template = "https://s3.amazonaws.com/cf-templates-158gc87u1eu1y-us-east-1/ec2_goatherding_us-east.yaml"
    template_url = s.upload_template('/home/mike/ec2_goatherding_us-east.yaml')
    print(template_url)
    s.create_stack("test3", template_url)
